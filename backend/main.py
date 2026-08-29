from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import scan_qr, scan_screenshot, reports
import uuid

app = FastAPI(
    title="ScamShield AI API",
    description="Pre-payment risk scoring and multimodal threat analysis engine",
    version="1.0.0"
)

# CORS configuration to allow mobile app connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response

@app.get("/healthz", tags=["System"])
async def healthz():
    return {"status": "ok"}

@app.get("/readyz", tags=["System"])
async def readyz():
    return {"status": "ready"}

# Register all feature routers
app.include_router(reports.router, prefix="/api/v1")
app.include_router(scan_qr.router, prefix="/api/v1")
app.include_router(scan_screenshot.router, prefix="/api/v1")