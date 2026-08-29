from pydantic import BaseModel
from typing import List, Union, Dict, Literal, Optional

class QRScanRequest(BaseModel):
    vpa: Optional[str] = None
    amount: Optional[float] = None
    txn_type: Optional[str] = None
    qr_raw: Optional[str] = None

class Signal(BaseModel):
    code: str
    severity: Literal['info', 'caution', 'high']  # Ensures frontend doesn't crash on .toUpperCase()
    message: str

class ScanResponseEnvelope(BaseModel):
    request_id: str
    scanner: Literal['qr', 'vpa', 'screenshot', 'url', 'text', 'document']
    verdict: Literal['green', 'yellow', 'red', 'unable_to_verify']
    safety_score: int
    explanation: str
    signals: List[Signal]  # Must be a list of Signal objects
    recommended_actions: List[str]
    provider_status: Union[str, Dict[str, str]]
    can_report: bool