from fastapi import APIRouter, Request
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime
    obs_connected: bool
    recording: bool
    version: str


@router.get("/health", response_model=HealthResponse)
async def health_check(request: Request):
    """Health check endpoint"""
    obs_service = request.app.state.obs_service
    
    return HealthResponse(
        status="healthy" if obs_service.connected else "degraded",
        timestamp=datetime.now(),
        obs_connected=obs_service.connected,
        recording=obs_service.recording,
        version="2.0.0"
    )


@router.get("/ping")
async def ping():
    """Simple ping endpoint"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}
