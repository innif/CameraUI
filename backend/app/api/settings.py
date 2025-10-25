from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from datetime import time
from typing import List
from app.core.config import settings as app_settings

router = APIRouter()


class SettingsResponse(BaseModel):
    """Response model for settings"""
    start_time: time
    end_time: time
    shutdown_time: time
    weekdays: List[int]
    delete_age_days: float
    show_logo: bool
    obs_host: str
    obs_port: int


class SettingsUpdateRequest(BaseModel):
    """Request model for updating settings"""
    start_time: time | None = None
    end_time: time | None = None
    shutdown_time: time | None = None
    weekdays: List[int] | None = None
    delete_age_seconds: float | None = None
    show_logo: bool | None = None


@router.get("/", response_model=SettingsResponse)
async def get_settings(request: Request):
    """Get current application settings"""
    return SettingsResponse(
        start_time=app_settings.START_TIME,
        end_time=app_settings.END_TIME,
        shutdown_time=app_settings.SHUTDOWN_TIME,
        weekdays=app_settings.WEEKDAYS,
        delete_age_days=app_settings.DELETE_AGE_SECONDS / 86400,  # Convert to days
        show_logo=app_settings.SHOW_LOGO,
        obs_host=app_settings.OBS_HOST,
        obs_port=app_settings.OBS_PORT
    )


@router.put("/")
async def update_settings(
    settings_update: SettingsUpdateRequest,
    request: Request
):
    """Update application settings"""
    # Update settings
    if settings_update.start_time is not None:
        app_settings.START_TIME = settings_update.start_time
    
    if settings_update.end_time is not None:
        app_settings.END_TIME = settings_update.end_time
    
    if settings_update.shutdown_time is not None:
        app_settings.SHUTDOWN_TIME = settings_update.shutdown_time
    
    if settings_update.weekdays is not None:
        app_settings.WEEKDAYS = settings_update.weekdays
    
    if settings_update.delete_age_seconds is not None:
        app_settings.DELETE_AGE_SECONDS = settings_update.delete_age_seconds
    
    if settings_update.show_logo is not None:
        app_settings.SHOW_LOGO = settings_update.show_logo
        # Update OBS logo visibility
        obs_service = request.app.state.obs_service
        import asyncio
        await asyncio.to_thread(obs_service.set_logo, settings_update.show_logo)

    return {
        "success": True,
        "message": "Settings updated successfully (restart required to persist)"
    }
