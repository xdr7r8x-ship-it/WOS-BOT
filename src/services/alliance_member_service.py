import logging
from datetime import datetime
from typing import Optional
from database import get_db

logger = logging.getLogger(__name__)


def add_alliance_member(
    guild_id: str,
    alliance_id: int,
    player_id: str,
    rank: str,
    assigned_by: str,
    source: str = "MANUAL",
    external_id: str = None
) -> tuple[bool, str]:
    now = datetime.utcnow().isoformat()
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO alliance_members 
                   (guild_id, alliance_id, player_id, external_member_id, alliance_rank, status, source, assigned_by, assigned_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, 'ACTIVE', ?, ?, ?, ?)""",
                (guild_id, alliance_id, player_id, external_id, rank, source, assigned_by, now, now)
            )
            
            save_member_history(guild_id, player_id, None, alliance_id, "JOINED", source, assigned_by)
            save_rank_history(guild_id, alliance_id, player_id, None, rank, assigned_by, source)
            
            return True, f"Member {player_id} added to alliance"
    except Exception as e:
        logger.error(f"Failed to add alliance member: {e}")
        return False, str(e)


def get_alliance_member(guild_id: str, player_id: str) -> Optional[dict]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM alliance_members WHERE guild_id = ? AND player_id = ? AND status = 'ACTIVE'",
            (guild_id, player_id)
        )
        row = cursor.fetchone()
        return dict(row) if row else None


def get_alliance_members(guild_id: str, alliance_id: int) -> list:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT * FROM alliance_members 
               WHERE guild_id = ? AND alliance_id = ? AND status = 'ACTIVE'
               ORDER BY alliance_rank, player_id""",
            (guild_id, alliance_id)
        )
        return [dict(row) for row in cursor.fetchall()]


def update_member_rank(
    guild_id: str,
    player_id: str,
    new_rank: str,
    changed_by: str,
    source: str = "MANUAL"
) -> tuple[bool, str]:
    now = datetime.utcnow().isoformat()
    
    member = get_alliance_member(guild_id, player_id)
    if not member:
        return False, "Member not found"
    
    old_rank = member.get("alliance_rank", "R1")
    if old_rank == new_rank:
        return True, "Rank unchanged"
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE alliance_members SET alliance_rank = ?, updated_at = ?
               WHERE guild_id = ? AND player_id = ?""",
            (new_rank, now, guild_id, player_id)
        )
    
    save_rank_history(guild_id, member.get("alliance_id"), player_id, old_rank, new_rank, changed_by, source)
    
    return True, f"Rank updated from {old_rank} to {new_rank}"


def disable_member(guild_id: str, player_id: str, changed_by: str, source: str = "MANUAL") -> tuple[bool, str]:
    now = datetime.utcnow().isoformat()
    
    member = get_alliance_member(guild_id, player_id)
    if not member:
        return False, "Member not found"
    
    old_alliance_id = member.get("alliance_id")
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE alliance_members SET status = 'DISABLED', updated_at = ?
               WHERE guild_id = ? AND player_id = ?""",
            (now, guild_id, player_id)
        )
    
    save_member_history(guild_id, player_id, old_alliance_id, None, "REMOVED", source, changed_by)
    
    return True, f"Member {player_id} removed"


def move_member(
    guild_id: str,
    player_id: str,
    new_alliance_id: int,
    changed_by: str,
    source: str = "MANUAL"
) -> tuple[bool, str]:
    now = datetime.utcnow().isoformat()
    
    member = get_alliance_member(guild_id, player_id)
    if not member:
        return False, "Member not found"
    
    old_alliance_id = member.get("alliance_id")
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE alliance_members SET alliance_id = ?, updated_at = ?
               WHERE guild_id = ? AND player_id = ?""",
            (new_alliance_id, now, guild_id, player_id)
        )
    
    save_member_history(guild_id, player_id, old_alliance_id, new_alliance_id, "MOVED", source, changed_by)
    
    return True, f"Member {player_id} moved to new alliance"


def update_last_seen(guild_id: str, player_id: str):
    now = datetime.utcnow().isoformat()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE alliance_members SET last_seen_at = ?, updated_at = ?
               WHERE guild_id = ? AND player_id = ?""",
            (now, now, guild_id, player_id)
        )


def save_rank_history(
    guild_id: str,
    alliance_id: int,
    player_id: str,
    old_rank: str,
    new_rank: str,
    changed_by: str,
    source: str
):
    now = datetime.utcnow().isoformat()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO alliance_rank_history
               (guild_id, alliance_id, player_id, old_rank, new_rank, changed_by, source, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (guild_id, alliance_id, player_id, old_rank, new_rank, changed_by, source, now)
        )


def save_member_history(
    guild_id: str,
    player_id: str,
    old_alliance_id: int,
    new_alliance_id: int,
    action: str,
    source: str,
    changed_by: str
):
    now = datetime.utcnow().isoformat()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO alliance_member_history
               (guild_id, player_id, old_alliance_id, new_alliance_id, action, source, changed_by, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (guild_id, player_id, old_alliance_id, new_alliance_id, action, source, changed_by, now)
        )


def get_rank_history(guild_id: str, player_id: str, limit: int = 10) -> list:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT * FROM alliance_rank_history
               WHERE guild_id = ? AND player_id = ?
               ORDER BY created_at DESC LIMIT ?""",
            (guild_id, player_id, limit)
        )
        return [dict(row) for row in cursor.fetchall()]


def get_member_history(guild_id: str, player_id: str, limit: int = 10) -> list:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT * FROM alliance_member_history
               WHERE guild_id = ? AND player_id = ?
               ORDER BY created_at DESC LIMIT ?""",
            (guild_id, player_id, limit)
        )
        return [dict(row) for row in cursor.fetchall()]
