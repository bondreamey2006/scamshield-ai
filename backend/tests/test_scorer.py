# backend/tests/test_scorer.py
from backend.services.scoring import score_screenshot

def test_screenshot_scoring_clean():
    # Mock data for a clean receipt
    mock_forensics = {
        "status": "SUCCESS",
        "extracted_amount": 500.0,
        "ela_anomaly_score": 10.0,
        "signals": [{"code": "AMOUNT_MATCH", "severity": "success"}]
    }
    result = score_screenshot(mock_forensics, "test-req-1")
    assert result.verdict == "green"
    assert result.safety_score == 95

def test_screenshot_scoring_forged():
    # Mock data for an edited receipt (ELA > 45)
    mock_forensics = {
        "status": "SUCCESS",
        "extracted_amount": 10000.0,
        "ela_anomaly_score": 55.0,
        "signals": [{"code": "ELA_ANOMALY", "severity": "danger"}]
    }
    result = score_screenshot(mock_forensics, "test-req-2")
    assert result.verdict == "red"
    assert result.safety_score < 50