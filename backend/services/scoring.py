from typing import Tuple, List

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