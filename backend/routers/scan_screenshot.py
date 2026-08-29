# backend/routers/scan_screenshot.py
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request
from typing import Optional
import uuid
from backend.services.forensics import analyze_payment_proof
from backend.services.scoring import score_screenshot

router = APIRouter()

@router.post("/screenshot")
async def process_screenshot(
    request: Request,
    file: UploadFile = File(...),
    expected_amount: Optional[float] = Form(None)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image.")

    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    try:
        image_bytes = await file.read()
        forensics_data = analyze_payment_proof(image_bytes, expected_amount)
        final_envelope = score_screenshot(forensics_data, req_id)
        return final_envelope

    except Exception as e:
        print(f"Screenshot error: {e}")
        return {
            "request_id": req_id,
            "scanner": "screenshot",
            "verdict": "unable_to_verify",
            "safety_score": 50,
            "explanation": "Critical error processing image.",
            "signals": [],
            "recommended_actions": ["Upload a clearer image."],
            "provider_status": {"llm": "bypassed", "forensics": "error"},
            "can_report": False
        }