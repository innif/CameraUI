from fastapi import APIRouter, HTTPException, Request, Depends
from typing import Optional

from app.models.video import VideoFile

router = APIRouter()


@router.get("/status")
async def get_recording_status(request: Request):
    """Get current recording status"""
    obs_service = request.app.state.obs_service
    return obs_service.get_status()


@router.post("/start")
async def start_recording(request: Request):
    """Manually start recording"""
    scheduler = request.app.state.scheduler
    success = await scheduler.start_recording()

    if success:
        return {"success": True, "message": "Recording started"}
    else:
        raise HTTPException(status_code=500, detail="Failed to start recording")


@router.post("/stop")
async def stop_recording(request: Request):
    """Manually stop recording"""
    scheduler = request.app.state.scheduler
    success = await scheduler.stop_recording()

    if success:
        return {"success": True, "message": "Recording stopped"}
    else:
        raise HTTPException(status_code=500, detail="Failed to stop recording")


@router.get("/current")
async def get_current_recording(request: Request) -> Optional[VideoFile]:
    """Get currently recording file"""
    obs_service = request.app.state.obs_service
    return obs_service.current_file


@router.get("/preview")
async def get_preview_image(request: Request):
    """Get current preview image from OBS"""
    obs_service = request.app.state.obs_service

    try:
        screenshot = await obs_service.get_screenshot()

        if screenshot:
            return {"success": True, "image": screenshot}
        else:
            raise HTTPException(status_code=503, detail="Could not get screenshot from OBS")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
