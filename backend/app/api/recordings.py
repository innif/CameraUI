from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import FileResponse
from typing import Optional, List
from datetime import time
import os

from app.models.video import VideoFile

router = APIRouter()


@router.get("/status")
async def get_recording_status(request: Request):
    """Get current recording status"""
    obs_service = request.app.state.obs_service
    return obs_service.get_status()


@router.get("/next-scheduled")
async def get_next_scheduled_recording(request: Request):
    """Get information about the next scheduled recording"""
    scheduler = request.app.state.scheduler
    next_recording = scheduler.get_next_scheduled_recording()

    if next_recording:
        return next_recording
    else:
        return {"message": "Keine automatischen Aufnahmen geplant"}


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


# Video Management Endpoints
@router.get("/videos")
async def get_all_videos(request: Request) -> List[dict]:
    """Get all recorded videos"""
    file_service = request.app.state.file_service
    videos = file_service.get_all_files()

    # Convert to dict format with additional info
    video_list = []
    for video in videos:
        # Calculate actual video file duration if end_time is null (currently recording)
        duration = None
        if video.duration:
            duration = video.duration.total_seconds()
        else:
            # Get actual duration from video file
            actual_duration = await file_service.calculate_video_duration(video.filename)
            if actual_duration:
                duration = actual_duration

        video_dict = {
            "id": video.filename,
            "filename": video.filename,
            "start_time": video.start_time.isoformat(),
            "end_time": video.end_time.isoformat() if video.end_time else None,
            "duration": duration,
            "is_recording": video.is_recording
        }
        video_list.append(video_dict)

    return video_list


@router.get("/videos/{video_id}")
async def get_video_by_id(video_id: str, request: Request) -> dict:
    """Get video details by ID (filename)"""
    file_service = request.app.state.file_service
    video = file_service.get_file(video_id)

    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    # Get file size
    video_path = file_service.get_video_path(video_id)
    file_size = file_service.get_filesize(video_path) if os.path.exists(video_path) else 0

    # Calculate actual video file duration if end_time is null (currently recording)
    duration = None
    if video.duration:
        duration = video.duration.total_seconds()
    else:
        # Get actual duration from video file
        actual_duration = await file_service.calculate_video_duration(video_id)
        if actual_duration:
            duration = actual_duration

    return {
        "id": video.filename,
        "filename": video.filename,
        "start_time": video.start_time.isoformat(),
        "end_time": video.end_time.isoformat() if video.end_time else None,
        "duration": duration,
        "is_recording": video.is_recording,
        "size": file_size
    }


@router.get("/videos/{video_id}/frame")
async def get_video_frame(video_id: str, timestamp: float, request: Request):
    """Get a frame from a video at a specific timestamp (in seconds)"""
    file_service = request.app.state.file_service
    video = file_service.get_file(video_id)

    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    try:
        # Convert timestamp (seconds from start) to time object
        from datetime import timedelta
        timestamp_datetime = video.start_time + timedelta(seconds=timestamp)
        timestamp_time = timestamp_datetime.time()

        frame_base64 = await file_service.get_frame_at_time(video_id, timestamp_time)

        if frame_base64:
            return {
                "success": True,
                "frame": frame_base64,
                "timestamp": timestamp
            }
        else:
            raise HTTPException(status_code=500, detail="Could not extract frame")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/videos/{video_id}/export")
async def export_video_subclip(video_id: str, request: Request):
    """Export a subclip from a video"""
    file_service = request.app.state.file_service
    video = file_service.get_file(video_id)

    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    try:
        # Parse request body
        body = await request.json()
        start_time_seconds = body.get("start_time", 0)
        end_time_seconds = body.get("end_time")

        if end_time_seconds is None:
            raise HTTPException(status_code=400, detail="end_time is required")

        # Convert seconds to time objects
        from datetime import timedelta
        start_datetime = video.start_time + timedelta(seconds=start_time_seconds)
        end_datetime = video.start_time + timedelta(seconds=end_time_seconds)

        start_time = start_datetime.time()
        end_time = end_datetime.time()

        # Export subclip
        output_path = await file_service.export_subclip(video_id, start_time, end_time)

        if output_path:
            # Get filename and file size
            output_filename = os.path.basename(output_path)
            file_size = file_service.get_filesize(output_path)

            return {
                "success": True,
                "file": {
                    "filename": output_filename,
                    "size": file_size,
                    "url": f"/videos/{output_filename}"
                }
            }
        else:
            raise HTTPException(status_code=500, detail="Export failed")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/videos/{video_id}/download")
async def download_video(video_id: str, request: Request):
    """Download a video file with streaming support"""
    file_service = request.app.state.file_service
    video = file_service.get_file(video_id)

    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    video_path = file_service.get_video_path(video_id)

    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Video file not found on disk")

    # Use FileResponse for efficient streaming of large files
    # This automatically handles Range requests for resumable downloads
    return FileResponse(
        path=video_path,
        media_type="video/mp4",
        filename=f"{video_id}.mp4",
        headers={
            "Accept-Ranges": "bytes",
            "Cache-Control": "no-cache"
        }
    )


@router.delete("/videos/{video_id}")
async def delete_video(video_id: str, request: Request):
    """Delete a video file"""
    file_service = request.app.state.file_service

    success = await file_service.delete_file(video_id)

    if success:
        return {"success": True, "message": f"Video {video_id} deleted"}
    else:
        raise HTTPException(status_code=500, detail="Failed to delete video")
