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
    pass


@router.get("/ping")
async def ping():
    """Simple ping endpoint"""
    return {"status": "ok"}
