from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class MuteRequest(BaseModel):
    """Request to mute/unmute recording"""
    muted: bool


class LogoRequest(BaseModel):
    """Request to show/hide logo"""
    visible: bool


@router.get("/status")
async def get_admin_status(request: Request):
    """Get admin status including OBS connection, recording state, audio monitor, etc."""
    obs_service = request.app.state.obs_service
    file_service = request.app.state.file_service
    audio_monitor = request.app.state.audio_monitor

    return {
        "obs": obs_service.get_status(),
        "files": {
            "total": len(file_service.get_all_files()),
            "newest": file_service.get_newest_file()
        },
        "audio_monitor": audio_monitor.get_status()
    }


@router.post("/mute")
async def set_mute_state(mute_request: MuteRequest, request: Request):
    """Mute or unmute the video recording"""
    obs_service = request.app.state.obs_service

    try:
        if mute_request.muted:
            obs_service.mute_video()
        else:
            obs_service.unmute_video()

        return {"success": True, "muted": mute_request.muted}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/camera/reload")
async def reload_camera(request: Request):
    """Reload the camera source in OBS"""
    obs_service = request.app.state.obs_service

    try:
        obs_service.reload_camera()
        return {"success": True, "message": "Camera reloaded"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/logo")
async def set_logo_visibility(logo_request: LogoRequest, request: Request):
    """Set logo visibility"""
    obs_service = request.app.state.obs_service

    try:
        obs_service.set_logo(logo_request.visible)
        return {"success": True, "visible": logo_request.visible}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/shutdown")
async def shutdown_system(request: Request):
    """Shutdown the system (use with caution!)"""
    import subprocess
    import logging

    logger = logging.getLogger(__name__)

    try:
        logger.warning("System shutdown initiated via API")

        # Use sudo shutdown command
        subprocess.run(["sudo", "shutdown", "-h", "now"], check=True)

        return {"success": True, "message": "System shutdown initiated"}
    except Exception as e:
        logger.error(f"Failed to shutdown system: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to shutdown: {str(e)}")


@router.post("/restart")
async def restart_system(request: Request):
    """Restart the system (use with caution!)"""
    import subprocess
    import logging

    logger = logging.getLogger(__name__)

    try:
        logger.warning("System restart initiated via API")

        # Use sudo reboot command
        subprocess.run(["sudo", "reboot"], check=True)

        return {"success": True, "message": "System restart initiated"}
    except Exception as e:
        logger.error(f"Failed to restart system: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to restart: {str(e)}")


@router.get("/audio/check")
async def check_audio_levels(request: Request):
    """Check audio levels from OBS (manual check)"""
    obs_service = request.app.state.obs_service

    try:
        audio_range = await obs_service.check_audio()
        return {
            "success": True,
            "range": audio_range,
            "has_audio": audio_range > 0.01  # Threshold for detecting audio
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/audio/monitor")
async def get_audio_monitor_status(request: Request):
    """Get the status of the automatic audio monitoring service"""
    audio_monitor = request.app.state.audio_monitor

    try:
        return audio_monitor.get_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/logs")
async def list_log_files(request: Request):
    """List available log files"""
    from pathlib import Path

    log_dir = Path("logs")

    if not log_dir.exists():
        return {"logs": []}

    try:
        log_files = [
            {
                "filename": f.name,
                "size": f.stat().st_size,
                "modified": f.stat().st_mtime
            }
            for f in log_dir.glob("*.log")
        ]

        # Sort by modified time, newest first
        log_files.sort(key=lambda x: x["modified"], reverse=True)

        return {"logs": log_files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/logs/{filename}")
async def get_log_file(filename: str, request: Request):
    """Get contents of a specific log file"""
    from pathlib import Path

    # Security: Prevent directory traversal
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    log_dir = Path("logs")
    log_path = log_dir / filename

    # Check if file exists and is in the logs directory
    if not log_path.exists() or not log_path.is_file():
        raise HTTPException(status_code=404, detail="Log file not found")

    # Verify the file is actually in the logs directory (security check)
    if not str(log_path.resolve()).startswith(str(log_dir.resolve())):
        raise HTTPException(status_code=400, detail="Invalid log file path")

    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return {
            "filename": filename,
            "content": content,
            "size": log_path.stat().st_size
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/logs")
async def delete_all_logs(request: Request):
    """Delete all log files"""
    from pathlib import Path
    import logging

    logger = logging.getLogger(__name__)
    log_dir = Path("logs")

    if not log_dir.exists():
        return {"success": True, "deleted": 0}

    try:
        deleted_count = 0
        for log_file in log_dir.glob("*.log"):
            try:
                log_file.unlink()
                deleted_count += 1
                logger.info(f"Deleted log file: {log_file.name}")
            except Exception as e:
                logger.error(f"Failed to delete {log_file.name}: {e}")

        return {
            "success": True,
            "deleted": deleted_count,
            "message": f"Deleted {deleted_count} log files"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
