from fastapi import APIRouter, Request
from urllib.parse import urlparse, parse_qs
from config.schemas import ScanResponse, QRScanRequest
from services.scoring import calculate_risk_score
import uuid

router = APIRouter(prefix="/scan", tags=["QR / VPA Scanner"])

MOCK_VPA_REGISTRY = {
    "merchant@okhdfcbank": {"is_verified": True, "reports": 0},
    "scammer@upi": {"is_verified": False, "reports": 4},
    "unknown_vendor@axis": {"is_verified": False, "reports": 0}
}

def parse_upi_uri(uri: str) -> dict:
    if not uri or not uri.startswith("upi://pay"):
        return {}
    parsed = urlparse(uri)
    params = parse_qs(parsed.query)
    return {k: v[0] for k, v in params.items()}

@router.post("/qr", response_model=ScanResponse)
async def scan_qr(payload: QRScanRequest, request: Request):
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    
    vpa = payload.vpa
    amount = payload.amount
    txn_type = payload.txn_type or "pay"

    if payload.qr_raw:
        parsed_params = parse_upi_uri(payload.qr_raw)
        vpa = parsed_params.get("pa", vpa)
        if "am" in parsed_params:
            try:
                amount = float(parsed_params["am"])
            except ValueError:
                pass
        if "mode" in parsed_params and parsed_params["mode"].lower() == "02":
            txn_type = "collect"

    if not vpa:
        return ScanResponse(
            request_id=req_id,
            scanner="qr",
            verdict="unable_to_verify",
            safety_score=None,
            explanation="Invalid or unreadable QR code. No Virtual Payment Address (VPA) detected.",
            signals=["MALFORMED_PAYLOAD"],
            recommended_actions=["Re-scan the QR code or manually verify the merchant."],
            provider_status="ok",
            can_report=False
        )

    record = MOCK_VPA_REGISTRY.get(vpa, {"is_verified": False, "reports": 0})
    is_verified = record["is_verified"]
    report_count = record["reports"]

    score, verdict, signals = calculate_risk_score(
        is_verified=is_verified,
        report_count=report_count,
        txn_type=txn_type
    )

    if verdict == "green":
        explanation = f"Verified merchant ({vpa}). Standard payment request with zero reported risk."
        actions = ["Review transaction details and proceed with payment."]
    elif verdict == "yellow":
        explanation = f"Unverified account ({vpa}) with no prior transaction history. Caution advised."
        actions = ["Verify payee identity independently before sending funds."]
    else:
        explanation = f"High risk detected. This transaction exhibits risk flags: {', '.join(signals)}."
        actions = ["Do not authorize payment.", "Report this VPA as fraudulent."]

    return ScanResponse(
        request_id=req_id,
        scanner="qr",
        verdict=verdict,
        safety_score=score,
        explanation=explanation,
        signals=signals,
        recommended_actions=actions,
        provider_status="ok",
        can_report=True
    )

@router.post("/vpa", response_model=ScanResponse)
async def scan_vpa(payload: QRScanRequest, request: Request):
    payload.txn_type = "pay"
    return await scan_qr(payload, request)