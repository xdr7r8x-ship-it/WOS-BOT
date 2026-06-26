import logging
import re
from datetime import datetime
from typing import Optional
from database import get_db

logger = logging.getLogger(__name__)


def validate_player_id(player_id: str) -> tuple[bool, str]:
    if not player_id:
        return False, "Player ID cannot be empty"
    
    player_id = str(player_id).strip()
    
    if not re.match(r"^\d{6,15}$", player_id):
        return False, "Player ID must be 6-15 digits"
    
    return True, ""


def register_player_id(guild_id: str, discord_user_id: str, player_id: str) -> tuple[bool, str]:
    valid, error = validate_player_id(player_id)
    if not valid:
        return False, error
    
    now = datetime.utcnow().isoformat()
    
    existing = get_player_id(guild_id, discord_user_id)
    if existing:
        return False, "Player ID already registered"
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO player_id_owners 
                   (guild_id, discord_user_id, player_id, status, created_at, updated_at)
                   VALUES (?, ?, ?, 'ACTIVE', ?, ?)""",
                (guild_id, discord_user_id, player_id, now, now)
            )
            
            cursor.execute(
                """INSERT INTO player_id_self_service_audit 
                   (guild_id, discord_user_id, action, old_player_id, new_player_id, status, created_at)
                   VALUES (?, ?, 'REGISTER', NULL, ?, 'SUCCESS', ?)""",
                (guild_id, discord_user_id, player_id, now)
            )
        
        return True, "Player ID registered"
    except Exception as e:
        logger.error(f"Error registering player ID: {e}")
        return False, "Failed to register Player ID"


def update_player_id(guild_id: str, discord_user_id: str, new_player_id: str) -> tuple[bool, str]:
    valid, error = validate_player_id(new_player_id)
    if not valid:
        return False, error
    
    now = datetime.utcnow().isoformat()
    
    existing = get_player_id(guild_id, discord_user_id)
    if not existing:
        return False, "No Player ID registered"
    
    if existing["discord_user_id"] != discord_user_id:
        return False, "Cannot update another user's Player ID"
    
    old_player_id = existing["player_id"]
    
    if old_player_id == new_player_id:
        return True, "No change needed"
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE player_id_owners SET player_id = ?, updated_at = ?
                   WHERE guild_id = ? AND discord_user_id = ?""",
                (new_player_id, now, guild_id, discord_user_id)
            )
            
            cursor.execute(
                """INSERT INTO player_id_self_service_audit 
                   (guild_id, discord_user_id, action, old_player_id, new_player_id, status, created_at)
                   VALUES (?, ?, 'UPDATE', ?, ?, 'SUCCESS', ?)""",
                (guild_id, discord_user_id, old_player_id, new_player_id, now)
            )
        
        return True, "Player ID updated"
    except Exception as e:
        logger.error(f"Error updating player ID: {e}")
        return False, "Failed to update Player ID"


def delete_player_id(guild_id: str, discord_user_id: str) -> tuple[bool, str]:
    now = datetime.utcnow().isoformat()
    
    existing = get_player_id(guild_id, discord_user_id)
    if not existing:
        return False, "No Player ID registered"
    
    if existing["discord_user_id"] != discord_user_id:
        return False, "Cannot delete another user's Player ID"
    
    old_player_id = existing["player_id"]
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE player_id_owners SET status = 'DELETED', updated_at = ?
                   WHERE guild_id = ? AND discord_user_id = ?""",
                (now, guild_id, discord_user_id)
            )
            
            cursor.execute(
                """INSERT INTO player_id_self_service_audit 
                   (guild_id, discord_user_id, action, old_player_id, new_player_id, status, created_at)
                   VALUES (?, ?, 'DELETE', ?, NULL, 'SUCCESS', ?)""",
                (guild_id, discord_user_id, old_player_id, now)
            )
        
        return True, "Player ID deleted"
    except Exception as e:
        logger.error(f"Error deleting player ID: {e}")
        return False, "Failed to delete Player ID"


def get_player_id(guild_id: str, discord_user_id: str) -> Optional[dict]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id, discord_user_id, player_id, status, created_at, updated_at
               FROM player_id_owners 
               WHERE guild_id = ? AND discord_user_id = ? AND status = 'ACTIVE'""",
            (guild_id, discord_user_id)
        )
        row = cursor.fetchone()
        if row:
            return {
                "id": row[0],
                "discord_user_id": row[1],
                "player_id": row[2],
                "status": row[3],
                "created_at": row[4],
                "updated_at": row[5],
            }
    return None


def get_user_player_id(guild_id: str, discord_user_id: str) -> Optional[str]:
    player = get_player_id(guild_id, discord_user_id)
    return player["player_id"] if player else None


def cleanup_player_id_on_leave(guild_id: str, discord_user_id: str):
    settings = get_panel_settings(guild_id)
    if not settings.get("allow_delete_own", True):
        return
    
    delete_player_id(guild_id, discord_user_id)


def get_panel_settings(guild_id: str) -> dict:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT panel_channel_id, require_confirmation, allow_delete_own
               FROM player_id_panel_settings WHERE guild_id = ?""",
            (guild_id,)
        )
        row = cursor.fetchone()
        if row:
            return {
                "panel_channel_id": row[0],
                "require_confirmation": bool(row[1]),
                "allow_delete_own": bool(row[2]),
            }
    return {
        "panel_channel_id": None,
        "require_confirmation": True,
        "allow_delete_own": True,
    }


def set_panel_settings(guild_id: str, panel_channel_id: str = None, require_confirmation: bool = None, allow_delete_own: bool = None) -> bool:
    now = datetime.utcnow().isoformat()
    current = get_panel_settings(guild_id)
    
    panel_channel_id = panel_channel_id if panel_channel_id is not None else current["panel_channel_id"]
    require_confirmation = require_confirmation if require_confirmation is not None else current["require_confirmation"]
    allow_delete_own = allow_delete_own if allow_delete_own is not None else current["allow_delete_own"]
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO player_id_panel_settings 
                   (guild_id, panel_channel_id, require_confirmation, allow_delete_own, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?)
                   ON CONFLICT(guild_id) 
                   DO UPDATE SET panel_channel_id = ?, require_confirmation = ?, allow_delete_own = ?, updated_at = ?""",
                (guild_id, panel_channel_id, require_confirmation, allow_delete_own, now, now,
                 panel_channel_id, require_confirmation, allow_delete_own, now)
            )
        return True
    except Exception as e:
        logger.error(f"Error setting panel settings: {e}")
        return False


def get_self_service_audit(guild_id: str, discord_user_id: str = None, limit: int = 50) -> list[dict]:
    with get_db() as conn:
        cursor = conn.cursor()
        if discord_user_id:
            cursor.execute(
                """SELECT discord_user_id, action, old_player_id, new_player_id, status, created_at
               FROM player_id_self_service_audit 
               WHERE guild_id = ? AND discord_user_id = ?
               ORDER BY created_at DESC LIMIT ?""",
                (guild_id, discord_user_id, limit)
            )
        else:
            cursor.execute(
                """SELECT discord_user_id, action, old_player_id, new_player_id, status, created_at
               FROM player_id_self_service_audit 
               WHERE guild_id = ?
               ORDER BY created_at DESC LIMIT ?""",
                (guild_id, limit)
            )
        return [dict(row) for row in cursor.fetchall()]
