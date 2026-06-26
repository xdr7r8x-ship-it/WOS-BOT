from datetime import datetime, timedelta
from typing import Optional


def now_iso() -> str:
    return datetime.utcnow().isoformat()


def now_timestamp() -> float:
    return datetime.utcnow().timestamp()


def from_iso(iso_str: str) -> Optional[datetime]:
    try:
        return datetime.fromisoformat(iso_str)
    except (ValueError, TypeError):
        return None


def format_duration(seconds: float) -> str:
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        return f"{int(seconds // 60)}m"
    elif seconds < 86400:
        return f"{int(seconds // 3600)}h"
    else:
        return f"{int(seconds // 86400)}d"


def format_uptime(seconds: float) -> str:
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    return " ".join(parts) if parts else "0m"


def is_older_than(iso_str: str, seconds: int) -> bool:
    dt = from_iso(iso_str)
    if dt is None:
        return False
    return (datetime.utcnow() - dt).total_seconds() > seconds


def add_seconds(iso_str: str, seconds: int) -> str:
    dt = from_iso(iso_str)
    if dt is None:
        return now_iso()
    return (dt + timedelta(seconds=seconds)).isoformat()
