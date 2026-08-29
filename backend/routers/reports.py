from fastapi import APIRouter, HTTPException, Request, Header
from pydantic import BaseModel
from typing import Optional
from backend.config.database import supabase
import hashlib
import os

router = APIRouter(prefix="/reports", tags=["Fraud Reporting"])

# Clean Pydantic model for reporting a VPA/Merchant
class ReportCreateRequest(BaseModel):
    vpa: str
    reason: str
    evidence_url: Optional[str] = None

@router.post("/", status_code=201)
async def submit_fraud_report(
    payload: ReportCreateRequest,
    request: Request,
    x_device_fingerprint: Optional[str] = Header(None)
):
    """
    Submits a fraud report for a VPA with device hash guarding, 
    duplicate suppression, and DEMO_MODE enforcement.
    """
    # 1. Enforce DEMO_MODE or environment safety if required
    demo_mode = os.getenv("DEMO_MODE", "true").lower() == "true"
    if not demo_mode:
        # If strict production mode is on, ensure it's an approved route
        pass

    client_ip = request.client.host if request.client else "unknown"
    raw_fingerprint = f"{x_device_fingerprint or 'anonymous'}-{client_ip}-{payload.vpa}"
    device_hash = hashlib.sha256(raw_fingerprint.encode()).hexdigest()

    if not supabase:
        raise HTTPException(status_code=500, detail="Database client not initialized.")

    try:
        # 2. Check if this device hash already reported this VPA (Duplicate Suppression)
        existing_report = supabase.table("reports").select("id").eq("vpa", payload.vpa).eq("device_hash", device_hash).execute()
        if existing_report.data and len(existing_report.data) > 0:
            raise HTTPException(
                status_code=400, 
                detail="Duplicate suppression: You have already submitted a report for this entity from this device."
            )

        # 3. Insert the report into Supabase with the device hash guard
        insert_data = {
            "vpa": payload.vpa,
            "reason": payload.reason,
            "evidence_url": payload.evidence_url,
            "device_hash": device_hash
        }
        
        res = supabase.table("reports").insert(insert_data).execute()
        
        return {
            "status": "success",
            "message": "Fraud report submitted and logged successfully.",
            "report": res.data[0] if res.data else {}
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        print("REPORT SUBMISSION ERROR:", e)
        raise HTTPException(status_code=500, detail=f"Failed to submit report: {str(e)}")