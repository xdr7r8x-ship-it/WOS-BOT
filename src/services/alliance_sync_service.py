import logging
from datetime import datetime
from typing import Optional
from database import get_db
from src.api.alliance_client import alliance_client
from src.utils.alliance_normalizer import normalize_member, map_external_rank
from src.utils.alliance_diff import compute_alliance_diff, has_changes
from src.services.alliance_service import (
    get_alliance_by_tag, get_alliance_members,
    save_alliance_audit, get_active_alliances
)
from src.services.alliance_member_service import (
    add_alliance_member, disable_member, update_member_rank,
    move_member, update_last_seen
)

logger = logging.getLogger(__name__)


def start_sync_run(guild_id: str, alliance_id: int, provider: str, started_by: str) -> int:
    now = datetime.utcnow().isoformat()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO alliance_sync_runs 
               (guild_id, alliance_id, provider, status, started_by, started_at)
               VALUES (?, ?, ?, 'RUNNING', ?, ?)""",
            (guild_id, alliance_id, provider, started_by, now)
        )
        return cursor.lastrowid


def complete_sync_run(
    run_id: int,
    status: str,
    added: int,
    removed: int,
    rank_changed: int,
    moved: int,
    error_message: str = None
):
    now = datetime.utcnow().isoformat()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE alliance_sync_runs 
               SET status = ?, completed_at = ?, 
                   added_count = ?, removed_count = ?, 
                   rank_changed_count = ?, moved_count = ?,
                   error_message = ?
               WHERE id = ?""",
            (status, now, added, removed, rank_changed, moved, error_message, run_id)
        )


async def sync_alliance(guild_id: str, alliance_tag: str, actor_id: str) -> dict:
    client = alliance_client
    provider_name = client.provider.provider_name
    
    alliance = get_alliance_by_tag(guild_id, alliance_tag)
    if not alliance:
        return {"success": False, "error": "Alliance not found"}
    
    alliance_id = alliance["id"]
    
    run_id = start_sync_run(guild_id, alliance_id, provider_name, actor_id)
    
    try:
        api_members = await client.fetch_alliance_members(alliance_tag)
        
        normalized_members = []
        for member in api_members:
            if "rank" in member and member["rank"] not in ["R1", "R2", "R3", "R4", "R5"]:
                member["rank"] = map_external_rank(member["rank"])
            normalized = normalize_member(member)
            if normalized:
                normalized_members.append(normalized)
        
        db_members = get_alliance_members(guild_id, alliance_id)
        
        diff = compute_alliance_diff(db_members, normalized_members, alliance_id)
        
        added_count = 0
        removed_count = 0
        rank_changed_count = 0
        moved_count = 0
        
        for added in diff.get("added", []):
            add_alliance_member(
                guild_id, alliance_id, added["player_id"],
                added["rank"], actor_id, source="SYNC"
            )
            added_count += 1
        
        for removed in diff.get("removed", []):
            disable_member(guild_id, removed["player_id"], actor_id, source="SYNC")
            removed_count += 1
        
        for rank_change in diff.get("rank_changed", []):
            update_member_rank(
                guild_id, rank_change["player_id"],
                rank_change["new_rank"], actor_id, source="SYNC"
            )
            rank_changed_count += 1
        
        for moved in diff.get("moved", []):
            move_member(
                guild_id, moved["player_id"],
                alliance_id, actor_id, source="SYNC"
            )
            moved_count += 1
        
        complete_sync_run(
            run_id, "COMPLETED",
            added_count, removed_count,
            rank_changed_count, moved_count
        )
        
        save_alliance_audit(
            guild_id, actor_id, "SYNC_COMPLETED", alliance_id,
            result="SUCCESS",
            metadata=f"Added:{added_count}, Removed:{removed_count}, RankChanged:{rank_changed_count}, Moved:{moved_count}"
        )
        
        return {
            "success": True,
            "run_id": run_id,
            "summary": diff["summary"]
        }
        
    except Exception as e:
        logger.error(f"Sync failed: {e}")
        complete_sync_run(run_id, "FAILED", 0, 0, 0, 0, str(e))
        save_alliance_audit(
            guild_id, actor_id, "SYNC_FAILED", alliance_id,
            result="FAILED", metadata=str(e)
        )
        return {"success": False, "error": str(e)}


async def run_auto_sync():
    client = alliance_client
    
    if not client.is_api_enabled:
        logger.info("Auto sync skipped: API disabled")
        return
    
    health = await client.health_check()
    if health.get("status") != "HEALTHY":
        logger.warning(f"Auto sync skipped: API unhealthy - {health.get('status')}")
        return
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT guild_id FROM guild_settings WHERE register_channel_id IS NOT NULL"
        )
        guilds = [row[0] for row in cursor.fetchall()]
    
    for guild_id in guilds:
        alliances = get_active_alliances(guild_id)
        for alliance in alliances:
            try:
                await sync_alliance(guild_id, alliance["alliance_tag"], "AUTO_SYNC")
            except Exception as e:
                logger.error(f"Auto sync failed for {alliance['alliance_tag']}: {e}")


def get_sync_history(guild_id: str, alliance_id: int = None, limit: int = 10) -> list:
    with get_db() as conn:
        cursor = conn.cursor()
        if alliance_id:
            cursor.execute(
                """SELECT * FROM alliance_sync_runs 
                   WHERE guild_id = ? AND alliance_id = ?
                   ORDER BY started_at DESC LIMIT ?""",
                (guild_id, alliance_id, limit)
            )
        else:
            cursor.execute(
                """SELECT * FROM alliance_sync_runs 
                   WHERE guild_id = ?
                   ORDER BY started_at DESC LIMIT ?""",
                (guild_id, limit)
            )
        return [dict(row) for row in cursor.fetchall()]
