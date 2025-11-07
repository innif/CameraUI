from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from app.core.config import settings
import logging
from datetime import datetime, timedelta
from typing import Dict, List

logger = logging.getLogger(__name__)

router = APIRouter()

# Rate limiting storage: {ip: [(timestamp, failed), ...]}
login_attempts: Dict[str, List[tuple]] = {}


class LoginRequest(BaseModel):
    """Login request model"""
    password: str


class LoginResponse(BaseModel):
    """Login response model"""
    success: bool
    message: str = ""


def clean_old_attempts(ip: str, window_minutes: int = 30):
    """Remove attempts older than the specified window"""
    if ip not in login_attempts:
        return

    cutoff_time = datetime.now() - timedelta(minutes=window_minutes)
    login_attempts[ip] = [
        (timestamp, failed) for timestamp, failed in login_attempts[ip]
        if timestamp > cutoff_time
    ]


def get_failed_attempts(ip: str, window_minutes: int = 5) -> int:
    """Get number of failed attempts in the last X minutes"""
    if ip not in login_attempts:
        return 0

    cutoff_time = datetime.now() - timedelta(minutes=window_minutes)
    return sum(
        1 for timestamp, failed in login_attempts[ip]
        if timestamp > cutoff_time and failed
    )


def get_cooldown_seconds(failed_count: int) -> int:
    """Calculate cooldown based on failed attempts"""
    if failed_count <= 1:
        return 2
    elif failed_count == 2:
        return 5
    elif failed_count == 3:
        return 10
    else:
        return 30


def is_rate_limited(ip: str) -> tuple[bool, int]:
    """Check if IP is rate limited, return (is_limited, seconds_to_wait)"""
    if ip not in login_attempts or not login_attempts[ip]:
        return False, 0

    # Get the most recent failed attempt
    recent_attempts = [
        (timestamp, failed) for timestamp, failed in login_attempts[ip]
        if failed
    ]

    if not recent_attempts:
        return False, 0

    recent_attempts.sort(reverse=True)
    last_failed_time, _ = recent_attempts[0]

    # Calculate how many failed attempts in last 5 minutes
    failed_count = get_failed_attempts(ip, window_minutes=5)

    if failed_count == 0:
        return False, 0

    cooldown_duration = get_cooldown_seconds(failed_count)
    time_since_last_attempt = (datetime.now() - last_failed_time).total_seconds()

    if time_since_last_attempt < cooldown_duration:
        remaining = int(cooldown_duration - time_since_last_attempt)
        return True, remaining

    return False, 0


def record_attempt(ip: str, failed: bool):
    """Record a login attempt"""
    if ip not in login_attempts:
        login_attempts[ip] = []

    # Clean old attempts first
    clean_old_attempts(ip, window_minutes=30)

    # Add new attempt
    login_attempts[ip].append((datetime.now(), failed))


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, http_request: Request):
    """
    Validate password for web access with rate limiting
    """
    try:
        # Get client IP
        client_ip = http_request.client.host

        # Check rate limit
        is_limited, wait_seconds = is_rate_limited(client_ip)
        if is_limited:
            logger.warning(f"Rate limit exceeded for IP {client_ip}, must wait {wait_seconds}s")
            raise HTTPException(
                status_code=429,
                detail=f"Zu viele Versuche. Bitte warte {wait_seconds} Sekunden."
            )

        # Compare with configured password
        if request.password == settings.WEB_PASSWORD:
            logger.info(f"Successful login attempt from {client_ip}")
            record_attempt(client_ip, failed=False)
            return LoginResponse(success=True, message="Login erfolgreich")
        else:
            logger.warning(f"Failed login attempt from {client_ip} - incorrect password")
            record_attempt(client_ip, failed=True)

            # Calculate how many failed attempts to inform user
            failed_count = get_failed_attempts(client_ip, window_minutes=5)
            cooldown = get_cooldown_seconds(failed_count)

            if cooldown > 0:
                return LoginResponse(
                    success=False,
                    message=f"Falsches Passwort. Nächster Versuch in {cooldown} Sekunden möglich."
                )
            else:
                return LoginResponse(success=False, message="Falsches Passwort")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Server error")
