from fastapi import APIRouter, HTTPException, Request
from typing import Optional, List
from datetime import datetime

from ..dependencies import require_auth, require_permission, log_web_action

router = APIRouter(prefix="/api/v1/reminders", tags=["reminders"])


@router.get("")
async def list_reminders(
    request: Request,
    status: Optional[str] = None,
    limit: int = 50
):
    require_auth(request)
    require_permission(request, "WEB_REMINDERS_VIEW")
    
    from database import get_reminders
    
    reminders = get_reminders(limit=limit)
    
    if status:
        reminders = [r for r in reminders if r.get("status") == status]
    
    return {"reminders": reminders}


@router.post("/bear")
async def create_bear_reminder(
    request: Request,
    event_name: str,
    event_time: str,
    offsets: List[int] = None
):
    require_auth(request)
    require_permission(request, "WEB_REMINDERS_MANAGE")
    
    log_web_action(request, "REMINDER_CREATE_BEAR", event_name, risk_level="MEDIUM")
    
    from database import add_reminder
    
    reminder = add_reminder(
        reminder_type="bear",
        event_name=event_name,
        event_time=event_time,
        offsets=offsets or [60, 30, 15],
        time_mode="GAME_TIME"
    )
    
    return reminder


@router.post("/event")
async def create_event_reminder(
    request: Request,
    event_name: str,
    event_time: str,
    offsets: List[int] = None,
    time_mode: str = "GAME_TIME"
):
    require_auth(request)
    require_permission(request, "WEB_REMINDERS_MANAGE")
    
    log_web_action(request, "REMINDER_CREATE_EVENT", event_name, risk_level="MEDIUM")
    
    from database import add_reminder
    
    reminder = add_reminder(
        reminder_type="event",
        event_name=event_name,
        event_time=event_time,
        offsets=offsets or [60, 30, 15],
        time_mode=time_mode
    )
    
    return reminder


@router.post("/custom")
async def create_custom_reminder(
    request: Request,
    name: str,
    message: str,
    schedule: str,
    time_mode: str = "REAL_TIME"
):
    require_auth(request)
    require_permission(request, "WEB_REMINDERS_MANAGE")
    
    log_web_action(request, "REMINDER_CREATE_CUSTOM", name, risk_level="MEDIUM")
    
    from database import add_reminder
    
    reminder = add_reminder(
        reminder_type="custom",
        event_name=name,
        event_time=schedule,
        offsets=[],
        time_mode=time_mode,
        message=message
    )
    
    return reminder


@router.patch("/{reminder_id}")
async def update_reminder(
    request: Request,
    reminder_id: int,
    event_name: Optional[str] = None,
    event_time: Optional[str] = None,
    offsets: Optional[List[int]] = None
):
    require_auth(request)
    require_permission(request, "WEB_REMINDERS_MANAGE")
    
    log_web_action(request, "REMINDER_UPDATE", str(reminder_id), risk_level="MEDIUM")
    
    from database import update_reminder
    
    reminder = update_reminder(reminder_id, event_name, event_time, offsets)
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    
    return reminder


@router.post("/{reminder_id}/disable")
async def disable_reminder(request: Request, reminder_id: int):
    require_auth(request)
    require_permission(request, "WEB_REMINDERS_MANAGE")
    
    log_web_action(request, "REMINDER_DISABLE", str(reminder_id), risk_level="LOW")
    
    from database import disable_reminder
    
    success = disable_reminder(reminder_id)
    return {"success": success}


@router.post("/{reminder_id}/test")
async def test_reminder(request: Request, reminder_id: int):
    require_auth(request)
    require_permission(request, "WEB_REMINDERS_MANAGE")
    
    log_web_action(request, "REMINDER_TEST", str(reminder_id), risk_level="LOW")
    
    return {"success": True, "message": "Test reminder sent"}


@router.get("/deliveries")
async def get_deliveries(request: Request, limit: int = 50):
    require_auth(request)
    require_permission(request, "WEB_REMINDERS_VIEW")
    
    from database import get_reminder_deliveries
    
    deliveries = get_reminder_deliveries(limit=limit)
    return {"deliveries": deliveries}


@router.get("/time-settings")
async def get_time_settings(request: Request):
    require_auth(request)
    require_permission(request, "WEB_REMINDERS_VIEW")
    
    from database import get_guild_settings
    
    settings = get_guild_settings("0")
    return {
        "game_timezone": settings.get("game_timezone", "UTC"),
        "real_timezone": settings.get("real_timezone", "UTC"),
        "display_timezone": settings.get("display_timezone", "UTC"),
        "default_time_mode": settings.get("default_time_mode", "GAME_TIME"),
    }


@router.patch("/time-settings")
async def update_time_settings(
    request: Request,
    game_timezone: Optional[str] = None,
    real_timezone: Optional[str] = None,
    display_timezone: Optional[str] = None,
    default_time_mode: Optional[str] = None
):
    require_auth(request)
    require_permission(request, "WEB_REMINDERS_MANAGE")
    
    from database import get_guild_settings, save_guild_settings
    
    settings = get_guild_settings("0")
    
    if game_timezone:
        settings["game_timezone"] = game_timezone
    if real_timezone:
        settings["real_timezone"] = real_timezone
    if display_timezone:
        settings["display_timezone"] = display_timezone
    if default_time_mode:
        settings["default_time_mode"] = default_time_mode
    
    save_guild_settings("0", settings)
    
    log_web_action(request, "TIME_SETTINGS_UPDATE", risk_level="LOW")
    
    return {"success": True}
