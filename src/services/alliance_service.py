import logging
from datetime import datetime
from typing import Optional
from database import get_db

logger = logging.getLogger(__name__)


def create_alliance(
    guild_id: str,
    alliance_tag: str,
    alliance_name: str,
    created_by: str,
    source: str = "MANUAL",
    external_id: str = None
) -> tuple[bool, str]:
    now = datetime.utcnow().isoformat()
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO alliances 
                   (guild_id, alliance_external_id, alliance_tag, alliance_name, status, source, created_by, created_at, updated_at)
                   VALUES (?, ?, ?, ?, 'ACTIVE', ?, ?, ?, ?)""",
                (guild_id, external_id, alliance_tag, alliance_name, source, created_by, now, now)
            )
            return True, f"Alliance {alliance_tag} created"
    except Exception as e:
        logger.error(f"Failed to create alliance: {e}")
        return False, str(e)


def get_alliance_by_tag(guild_id: str, alliance_tag: str) -> Optional[dict]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM alliances WHERE guild_id = ? AND alliance_tag = ?",
            (guild_id, alliance_tag)
        )
        row = cursor.fetchone()
        return dict(row) if row else None


def get_alliance_by_id(alliance_id: int) -> Optional[dict]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM alliances WHERE id = ?", (alliance_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_active_alliances(guild_id: str) -> list:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM alliances WHERE guild_id = ? AND status = 'ACTIVE' ORDER BY alliance_tag",
            (guild_id,)
        )
        return [dict(row) for row in cursor.fetchall()]


def update_alliance(
    alliance_id: int,
    alliance_name: str = None,
    status: str = None
) -> tuple[bool, str]:
    now = datetime.utcnow().isoformat()
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        if alliance_name:
            cursor.execute(
                "UPDATE alliances SET alliance_name = ?, updated_at = ? WHERE id = ?",
                (alliance_name, now, alliance_id)
            )
        
        if status:
            cursor.execute(
                "UPDATE alliances SET status = ?, updated_at = ? WHERE id = ?",
                (status, now, alliance_id)
            )
        
        return True, "Alliance updated"


def disable_alliance(alliance_id: int) -> tuple[bool, str]:
    return update_alliance(alliance_id, status="DISABLED")


def get_alliance_member_count(alliance_id: int) -> int:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM alliance_members WHERE alliance_id = ? AND status = 'ACTIVE'",
            (alliance_id,)
        )
        return cursor.fetchone()[0]


def save_alliance_audit(
    guild_id: str,
    actor_id: str,
    action: str,
    result: str,
    alliance_id: int = None,
    player_id: str = None,
    metadata: str = None
):
    now = datetime.utcnow().isoformat()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO alliance_audit_logs 
               (guild_id, actor_id, action, alliance_id, player_id, result, metadata, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (guild_id, actor_id, action, alliance_id, player_id, result, metadata, now)
        )
