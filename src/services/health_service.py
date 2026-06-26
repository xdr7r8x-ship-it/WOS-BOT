from datetime import datetime

from database import (
    get_queue_count,
    get_retry_job_count,
    get_player_count,
    get_total_success_count,
    get_total_failed_count,
    get_db_size,
    log_system,
)
from ..utils.rate_limit import rate_limiter


class HealthService:
    def __init__(self):
        self._last_error = None
        self._last_error_time = None

    def record_error(self, error: str):
        self._last_error = error
        self._last_error_time = datetime.utcnow().isoformat()

    def get_health(self, guild_id: str = None) -> dict:
        is_paused, pause_msg = rate_limiter.is_paused(str(guild_id) if guild_id else "default")
        
        queue_count = get_queue_count()
        retry_count = get_retry_job_count()
        success_count = get_total_success_count()
        failed_count = get_total_failed_count()
        db_size = get_db_size()
        
        player_count = 0
        if guild_id:
            from database import get_player_count
            player_count = get_player_count(str(guild_id))
        
        return {
            "status": "online",
            "queue_size": queue_count,
            "retry_jobs": retry_count,
            "active_players": player_count,
            "total_success": success_count,
            "total_failed": failed_count,
            "db_size": db_size,
            "api_status": "paused" if is_paused else "ok",
            "circuit_breaker": pause_msg if is_paused else "ok",
            "last_error": self._last_error,
            "last_error_time": self._last_error_time,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def format_health_embed(self, guild_id: str = None) -> dict:
        health = self.get_health(guild_id)
        
        lines = [
            f"**Bot Status:** {'🟢 Online' if health['status'] == 'online' else '🔴 Offline'}",
            f"**Queue:** {health['queue_size']}",
            f"**Retry Jobs:** {health['retry_jobs']}",
            f"**Active Players:** {health['active_players']}",
            f"**API Status:** {'🟡 ' + health['circuit_breaker'] if health['api_status'] == 'paused' else '🟢 OK'}",
            f"**DB Size:** {health['db_size']}",
            f"**Success Count:** {health['total_success']}",
            f"**Failed Count:** {health['total_failed']}",
        ]
        
        if health['last_error']:
            lines.append(f"**Last Error:** {health['last_error'][:100]}")
        
        return {
            "title": "🟢 Bot Health",
            "description": "\n".join(lines),
            "color": 0x00FF00 if health['status'] == 'online' else 0xFF0000,
        }


health_service = HealthService()
