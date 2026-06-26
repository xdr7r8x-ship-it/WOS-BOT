import psutil
import os
from datetime import datetime
from typing import Dict, Any


_bot_start_time = datetime.utcnow()


def get_bot_status() -> Dict[str, Any]:
    uptime = (datetime.utcnow() - _bot_start_time).total_seconds()
    
    return {
        "status": "online",
        "uptime_seconds": int(uptime),
        "pid": os.getpid(),
    }


def get_health_status() -> Dict[str, Any]:
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        "healthy": True,
        "memory_percent": memory.percent,
        "memory_used_mb": memory.used // (1024 * 1024),
        "memory_total_mb": memory.total // (1024 * 1024),
        "disk_percent": disk.percent,
        "disk_used_gb": disk.used // (1024 * 1024 * 1024),
        "disk_total_gb": disk.total // (1024 * 1024 * 1024),
    }


def get_dashboard_summary() -> Dict[str, Any]:
    from database import get_player_count, get_active_players, get_code_stats, get_reminder_stats
    
    players = get_active_players()
    
    return {
        "bot_status": "online",
        "players_count": get_player_count(),
        "active_players": len(players),
        "code_stats": get_code_stats(),
        "reminder_stats": get_reminder_stats(),
        "health": get_health_status(),
    }
