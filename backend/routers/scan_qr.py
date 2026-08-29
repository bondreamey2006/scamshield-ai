from fastapi import APIRouter, Request
from urllib.parse import urlparse, parse_qs
from backend.config.schemas import ScanResponseEnvelope, QRScanRequest, Signal
from backend.services.scoring import calculate_risk_score
from backend.services.explainer import generate_explanation
from backend.config.database import supabase
import uuid

router = APIRouter(prefix="/scan", tags=["QR / VPA Scanner"])

def parse_upi_uri(uri: str) -> dict:
    if not uri or not uri.startswith("upi://pay"):
        return {}
    parsed = urlparse(uri)
    params = parse_qs(parsed.query)
    return {k: v[0] for k, v in params.items()}

@router.post("/qr", response_model=ScanResponseEnvelope)
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
        return ScanResponseEnvelope(
            request_id=req_id,
            scanner="qr",
            verdict="unable_to_verify",
            safety_score=50,
            explanation="Invalid or unreadable QR code. No VPA detected.",
            signals=[Signal(code="MALFORMED_PAYLOAD", severity="high", message="No valid VPA found in payload.")],
            recommended_actions=["Re-scan the QR code or manually verify."],
            provider_status="ok",
            can_report=False
        )

    is_verified = False
    report_count = 0

    if supabase:
        try:
            vpa_res = supabase.table("vpas").select("*").eq("vpa_normalized", vpa).execute()
            if vpa_res.data:
                vpa_record = vpa_res.data[0]
                is_verified = vpa_record.get("trusted_record", False)
                vpa_id = vpa_record.get("id")
                
                rep_res = supabase.table("reports").select("id").eq("vpa_id", vpa_id).execute()
                report_count = len(rep_res.data)
        except Exception as e:
            print("SUPABASE ERROR EXCEPTION:", e)

    score, verdict, raw_signals = calculate_risk_score(
        is_verified=is_verified,
        report_count=report_count,
        txn_type=txn_type
    )

    explanation = await generate_explanation(verdict, score, raw_signals)

    # Map raw string signals into structured Signal objects matching frontend contract
    structured_signals = []
    for sig in raw_signals:
        sev = "high" if verdict == "red" else ("caution" if verdict == "yellow" else "info")
        structured_signals.append(Signal(code=sig, severity=sev, message=f"Signal triggered: {sig}"))

    if verdict == "green":
        actions = ["Review transaction details and proceed with payment."]
    elif verdict == "yellow":
        actions = ["Verify payee identity independently before sending funds."]
    else:
        actions = ["Do not authorize payment.", "Report this VPA as fraudulent."]

    return ScanResponseEnvelope(
        request_id=req_id,
        scanner="qr",
        verdict=verdict,
        safety_score=score,
        explanation=explanation,
        signals=structured_signals,
        recommended_actions=actions,
        provider_status="ok",
        can_report=True
    )

@router.post("/vpa", response_model=ScanResponseEnvelope)
async def scan_vpa(payload: QRScanRequest, request: Request):
    payload.txn_type = "pay"
    return await scan_qr(payload, request)