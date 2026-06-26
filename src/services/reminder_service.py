import logging
import asyncio
from datetime import datetime, timedelta
from typing import Optional, List
from database import get_db

logger = logging.getLogger(__name__)

REMINDER_TIME_MODES = ["GAME_TIME", "REAL_TIME"]
REMINDER_RECURRENCES = ["NONE", "DAILY", "WEEKLY", "CUSTOM"]
DEFAULT_OFFSETS = [60, 15, 0]


def get_time_settings(guild_id: str) -> dict:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT game_timezone, real_timezone, display_timezone 
               FROM reminder_time_settings WHERE guild_id = ?""",
            (guild_id,)
        )
        row = cursor.fetchone()
        if row:
            return {
                "game_timezone": row[0],
                "real_timezone": row[1],
                "display_timezone": row[2],
            }
    return {
        "game_timezone": "UTC",
        "real_timezone": "Asia/Riyadh",
        "display_timezone": "Asia/Riyadh",
    }


def set_time_settings(guild_id: str, game_timezone: str = None, real_timezone: str = None, display_timezone: str = None) -> bool:
    now = datetime.utcnow().isoformat()
    current = get_time_settings(guild_id)
    
    game_timezone = game_timezone or current["game_timezone"]
    real_timezone = real_timezone or current["real_timezone"]
    display_timezone = display_timezone or current["display_timezone"]
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO reminder_time_settings (guild_id, game_timezone, real_timezone, display_timezone, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?)
                   ON CONFLICT(guild_id) 
                   DO UPDATE SET game_timezone = ?, real_timezone = ?, display_timezone = ?, updated_at = ?""",
                (guild_id, game_timezone, real_timezone, display_timezone, now, now, game_timezone, real_timezone, display_timezone, now)
            )
        return True
    except Exception as e:
        logger.error(f"Error saving time settings: {e}")
        return False


def create_reminder(
    guild_id: str,
    channel_id: str,
    event_name: str,
    event_time_local: str,
    event_time_utc: str,
    source_timezone: str,
    time_mode: str,
    recurrence: str,
    role_id: str,
    created_by: str,
    offsets: List[int] = None
) -> tuple[bool, int]:
    now = datetime.utcnow().isoformat()
    
    if offsets is None:
        offsets = DEFAULT_OFFSETS.copy()
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO event_reminders 
                   (guild_id, channel_id, event_name, event_time_local, event_time_utc, source_timezone, 
                    time_mode, recurrence, role_id, created_by, status, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'ACTIVE', ?, ?)""",
                (guild_id, channel_id, event_name, event_time_local, event_time_utc, source_timezone,
                 time_mode, recurrence, role_id, created_by, now, now)
            )
            reminder_id = cursor.lastrowid
            
            for offset in offsets:
                label = None
                if offset == 60:
                    label = "1 hour before"
                elif offset == 15:
                    label = "15 minutes before"
                elif offset == 0:
                    label = "At event time"
                
                cursor.execute(
                    """INSERT INTO event_reminder_offsets (reminder_id, offset_minutes, label, status, created_at)
                       VALUES (?, ?, ?, 'ACTIVE', ?)""",
                    (reminder_id, offset, label, now)
                )
            
            cursor.execute(
                """INSERT INTO event_reminder_audit_logs 
                   (guild_id, actor_id, action, reminder_id, result, risk_level, metadata, created_at)
                   VALUES (?, ?, 'REMINDER_CREATED', ?, 'SUCCESS', 'LOW', ?, ?)""",
                (guild_id, created_by, reminder_id, f'{{"event_name": "{event_name}"}}', now)
            )
        
        return True, reminder_id
    except Exception as e:
        logger.error(f"Error creating reminder: {e}")
        return False, 0


def get_reminders(guild_id: str, status: str = "ACTIVE") -> list[dict]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id, channel_id, event_name, event_time_local, event_time_utc, source_timezone,
                    time_mode, recurrence, role_id, status, created_at
               FROM event_reminders WHERE guild_id = ? AND status = ? ORDER BY event_time_utc""",
            (guild_id, status)
        )
        reminders = []
        for row in cursor.fetchall():
            cursor.execute(
                """SELECT offset_minutes, label FROM event_reminder_offsets 
                   WHERE reminder_id = ? AND status = 'ACTIVE'""",
                (row[0],)
            )
            offsets = [{"offset": o[0], "label": o[1]} for o in cursor.fetchall()]
            reminders.append({
                "id": row[0],
                "channel_id": row[1],
                "event_name": row[2],
                "event_time_local": row[3],
                "event_time_utc": row[4],
                "source_timezone": row[5],
                "time_mode": row[6],
                "recurrence": row[7],
                "role_id": row[8],
                "status": row[9],
                "created_at": row[10],
                "offsets": offsets,
            })
        return reminders


def get_upcoming_reminders(guild_id: str, limit: int = 10) -> list[dict]:
    now = datetime.utcnow().isoformat()
    reminders = get_reminders(guild_id, "ACTIVE")
    
    upcoming = []
    for r in reminders:
        event_time = datetime.fromisoformat(r["event_time_utc"])
        if event_time >= datetime.utcnow():
            upcoming.append(r)
    
    return upcoming[:limit]


def delete_reminder(guild_id: str, reminder_id: int, actor_id: str) -> tuple[bool, str]:
    now = datetime.utcnow().isoformat()
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE event_reminders SET status = 'DELETED', updated_at = ? WHERE id = ? AND guild_id = ?""",
                (now, reminder_id, guild_id)
            )
            
            cursor.execute(
                """INSERT INTO event_reminder_audit_logs 
                   (guild_id, actor_id, action, reminder_id, result, risk_level, created_at)
                   VALUES (?, ?, 'REMINDER_DELETED', ?, 'SUCCESS', 'MEDIUM', ?)""",
                (guild_id, actor_id, reminder_id, now)
            )
        return True, "Reminder deleted"
    except Exception as e:
        logger.error(f"Error deleting reminder: {e}")
        return False, str(e)


def record_delivery(
    reminder_id: int,
    offset_id: int,
    guild_id: str,
    channel_id: str,
    role_id: str,
    event_name: str,
    event_time_utc: str,
    delivery_time: str,
    status: str,
    error_message: str = None
) -> bool:
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO event_reminder_deliveries 
                   (reminder_id, offset_id, guild_id, channel_id, role_id, event_name, event_time_utc, 
                    delivery_time, status, error_message, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (reminder_id, offset_id, guild_id, channel_id, role_id, event_name, event_time_utc,
                 delivery_time, status, error_message, datetime.utcnow().isoformat())
            )
        return True
    except Exception as e:
        logger.error(f"Error recording delivery: {e}")
        return False


def get_failed_deliveries(guild_id: str, limit: int = 10) -> list[dict]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id, reminder_id, event_name, status, error_message, delivery_time, created_at
               FROM event_reminder_deliveries 
               WHERE guild_id = ? AND status = 'FAILED' 
               ORDER BY created_at DESC LIMIT ?""",
            (guild_id, limit)
        )
        return [dict(row) for row in cursor.fetchall()]


def save_reminder_audit(guild_id: str, actor_id: str, action: str, reminder_id: int, result: str, risk_level: str, metadata: str = None):
    now = datetime.utcnow().isoformat()
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO event_reminder_audit_logs 
                   (guild_id, actor_id, action, reminder_id, result, risk_level, metadata, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (guild_id, actor_id, action, reminder_id, result, risk_level, metadata, now)
            )
    except Exception as e:
        logger.warning(f"Error saving reminder audit: {e}")
