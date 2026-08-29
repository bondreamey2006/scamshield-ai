from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from uuid import uuid4

VerdictType = Literal["green", "yellow", "red", "unable_to_verify"]
ScannerType = Literal["qr", "screenshot", "url", "text"]
ProviderStatus = Literal["ok", "unavailable", "mock"]

class ScanResponse(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid4()))
    scanner: ScannerType
    verdict: VerdictType
    safety_score: Optional[int] = Field(None, ge=0, le=100)
    explanation: str
    signals: List[str] = Field(default_factory=list)
    recommended_actions: List[str] = Field(default_factory=list)
    provider_status: ProviderStatus = "ok"
    can_report: bool = True

class QRScanRequest(BaseModel):
    vpa: Optional[str] = None
    amount: Optional[float] = None
    txn_type: Optional[str] = "pay"
    qr_raw: Optional[str] = None

class ErrorResponse(BaseModel):
    request_id: str
    error_code: str
    message: str