from fastapi import APIRouter, HTTPException, Request, Depends
from typing import Optional

from app.models.video import VideoFile

router = APIRouter()


@router.get("/status")
async def get_recording_status(request: Request):
    """Get current recording status"""
    pass


@router.post("/start")
async def start_recording(request: Request):
    """Manually start recording"""
    pass


@router.post("/stop")
async def stop_recording(request: Request):
    """Manually stop recording"""
    pass


@router.get("/current")
async def get_current_recording(request: Request) -> Optional[VideoFile]:
    """Get currently recording file"""
    pass


@router.get("/preview")
async def get_preview_image(request: Request):
    """Get current preview image from OBS"""
    pass
