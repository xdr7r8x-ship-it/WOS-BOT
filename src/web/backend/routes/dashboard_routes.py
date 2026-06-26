from fastapi import APIRouter, HTTPException, Request
from typing import Dict, Any
import psutil
import os
from datetime import datetime
import asyncio

from ..dependencies import require_auth, require_permission
from ...services.bot_status_service import get_bot_status, get_health_status, get_dashboard_summary

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])


@router.get("/summary")
async def get_dashboard_summary_endpoint(request: Request):
    require_auth(request)
    require_permission(request, "WEB_DASHBOARD_VIEW")
    
    try:
        summary = get_dashboard_summary()
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get dashboard summary")


@router.get("/health")
async def get_health(request: Request):
    require_auth(request)
    require_permission(request, "WEB_DASHBOARD_VIEW")
    
    try:
        health = get_health_status()
        return health
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get health status")


@router.get("/live")
async def get_live_data(request: Request):
    require_auth(request)
    require_permission(request, "WEB_DASHBOARD_VIEW")
    
    try:
        status = get_bot_status()
        
        uptime_seconds = status.get("uptime_seconds", 0)
        days = uptime_seconds // 86400
        hours = (uptime_seconds % 86400) // 3600
        minutes = (uptime_seconds % 3600) // 60
        uptime_str = f"{days}d {hours}h {minutes}m"
        
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        from database import get_player_count, get_active_players, get_code_stats, get_reminder_stats
        
        return {
            "bot_status": status.get("status", "unknown"),
            "uptime": uptime_str,
            "players_count": get_player_count(),
            "active_players": len(get_active_players()),
            "code_stats": get_code_stats(),
            "reminder_stats": get_reminder_stats(),
            "memory_percent": memory.percent,
            "disk_percent": disk.percent,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get live data")
