from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class LoginRequest(BaseModel):
    """Login request model"""
    password: str


class LoginResponse(BaseModel):
    """Login response model"""
    success: bool
    message: str = ""


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Validate password for web access
    """
    try:
        # Compare with configured password
        if request.password == settings.WEB_PASSWORD:
            logger.info("Successful login attempt")
            return LoginResponse(success=True, message="Login erfolgreich")
        else:
            logger.warning("Failed login attempt - incorrect password")
            return LoginResponse(success=False, message="Falsches Passwort")

    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Server error")
