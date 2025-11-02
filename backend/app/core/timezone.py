"""
Timezone utilities for consistent timezone handling across the application.

This module provides utilities for:
- Converting between UTC and local timezone
- Getting current time in UTC or local timezone
- Formatting datetimes for display
"""

from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from app.core.config import settings


def get_local_timezone() -> ZoneInfo:
    """Get the configured local timezone"""
    return ZoneInfo(settings.TIMEZONE)


def now_utc() -> datetime:
    """Get current time in UTC with timezone info"""
    return datetime.now(timezone.utc)


def now_local() -> datetime:
    """Get current time in local timezone with timezone info"""
    return datetime.now(timezone.utc).astimezone(get_local_timezone())


def to_local(dt: datetime) -> datetime:
    """
    Convert a datetime to local timezone

    Args:
        dt: A datetime object (can be naive or aware)

    Returns:
        A timezone-aware datetime in the local timezone
    """
    if dt.tzinfo is None:
        # Naive datetime - assume it's UTC
        dt = dt.replace(tzinfo=timezone.utc)

    return dt.astimezone(get_local_timezone())


def to_utc(dt: datetime) -> datetime:
    """
    Convert a datetime to UTC

    Args:
        dt: A datetime object (can be naive or aware)

    Returns:
        A timezone-aware datetime in UTC
    """
    if dt.tzinfo is None:
        # Naive datetime - assume it's in local timezone
        local_tz = get_local_timezone()
        dt = dt.replace(tzinfo=local_tz)

    return dt.astimezone(timezone.utc)


def format_local(dt: datetime, format_string: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format a datetime in local timezone

    Args:
        dt: A datetime object
        format_string: strftime format string

    Returns:
        Formatted string in local timezone
    """
    local_dt = to_local(dt)
    return local_dt.strftime(format_string)


def format_german(dt: datetime) -> str:
    """
    Format a datetime in German format (DD.MM.YYYY HH:MM)

    Args:
        dt: A datetime object

    Returns:
        Formatted string like "25.10.2024 19:50"
    """
    local_dt = to_local(dt)
    return local_dt.strftime("%d.%m.%Y %H:%M")


def parse_iso(iso_string: str) -> datetime:
    """
    Parse an ISO format string to datetime

    Args:
        iso_string: ISO format datetime string

    Returns:
        A timezone-aware datetime in UTC
    """
    dt = datetime.fromisoformat(iso_string)
    return to_utc(dt)
