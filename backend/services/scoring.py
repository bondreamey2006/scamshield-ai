from typing import Tuple, List
from backend.config.schemas import ScanResponseEnvelope, Signal

def calculate_risk_score(
    is_verified: bool,
    report_count: int,
    txn_type: str,
    safe_browsing_flag: bool = False
) -> Tuple[int, str, List[str]]:
    score = 50
    signals = []

    if is_verified:
        score += 40
        signals.append("VERIFIED_MERCHANT")

    if report_count >= 3:
        score -= 40
        signals.append("HIGH_REPORTS_AUTO_RED")
    elif report_count > 0:
        score -= 20
        signals.append("HAS_RECENT_REPORTS")

    if txn_type and txn_type.lower() == "collect":
        score -= 25
        signals.append("DISGUISED_COLLECT_REQUEST")

    if safe_browsing_flag:
        score -= 50
        signals.append("MALICIOUS_LINK_DETECTED")

    score = max(0, min(100, score))

    if score >= 70:
        verdict = "green"
    elif score >= 40:
        verdict = "yellow"
    else:
        verdict = "red"

    return score, verdict, signals


def score_screenshot(forensics_result: dict, req_id: str) -> ScanResponseEnvelope:
    """
    Evaluates ELA anomaly scores and forensics signals to construct 
    the final ScanResponseEnvelope for payment screenshots.
    """
    status = forensics_result.get("status", "SUCCESS")
    extracted_amount = forensics_result.get("extracted_amount")
    ela_score = forensics_result.get("ela_anomaly_score", 0.0)
    raw_signals = forensics_result.get("signals", [])

    # If forensics cannot verify the image, bypass scoring and return unable_to_verify
    if status == "UNABLE_TO_VERIFY":
        return ScanResponseEnvelope(
            request_id=req_id,
            scanner="screenshot",
            verdict="unable_to_verify",
            safety_score=50,
            explanation="Could not extract readable text or payment proof from the image. Please upload a clearer screenshot.",
            signals=[Signal(code="OCR_FAILED", severity="caution", message="Failed to parse payment details from image.")],
            recommended_actions=["Upload a high-resolution, unedited screenshot of the payment receipt."],
            provider_status={"llm": "bypassed", "forensics": "unable_to_verify"},
            can_report=False
        )

    # Determine verdict and safety score based on ELA anomaly score (>45 is highly suspicious)
    if ela_score > 45.0 or any(s.get("severity") == "danger" for s in raw_signals):
        verdict = "red"
        safety_score = max(0, int(100 - ela_score))
        explanation = f"Critical image tampering detected. ELA anomaly score is high ({ela_score}/100), indicating potential digital manipulation."
        actions = ["Do not trust this payment receipt.", "Verify funds directly in your bank account app."]
    elif ela_score > 20.0:
        verdict = "yellow"
        safety_score = int(100 - (ela_score * 1.5))
        explanation = f"Moderate compression anomalies found ({ela_score}/100). Proceed with caution and verify transaction independently."
        actions = ["Cross-check the transaction ID with your financial provider."]
    else:
        verdict = "green"
        safety_score = 95
        explanation = "Payment screenshot appears authentic with minimal editing artifacts detected."
        actions = ["Receipt looks consistent. Proceed with standard verification."]

    # Normalize signals to match the frontend schema contract
    structured_signals = []
    for sig in raw_signals:
        sev_map = {"success": "info", "danger": "high", "warning": "caution"}
        frontend_sev = sev_map.get(sig.get("severity"), "caution")
        structured_signals.append(
            Signal(
                code=sig.get("code", "UNKNOWN"),
                severity=frontend_sev,
                message=sig.get("message", "")
            )
        )

    return ScanResponseEnvelope(
        request_id=req_id,
        scanner="screenshot",
        verdict=verdict,
        safety_score=safety_score,
        explanation=explanation,
        signals=structured_signals,
        recommended_actions=actions,
        provider_status={"llm": "active", "forensics": "success"},
        can_report=True
    )