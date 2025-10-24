from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from datetime import time
from typing import List

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
    pass


@router.put("/")
async def update_settings(
    settings_update: SettingsUpdateRequest,
    request: Request
):
    """Update application settings"""
    pass


@router.post("/reload")
async def reload_settings(request: Request):
    """Reload settings from file"""
    pass


@router.post("/save")
async def save_settings(request: Request):
    """Save current settings to file"""
    pass
