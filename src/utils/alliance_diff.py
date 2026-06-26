from typing import Optional
from dataclasses import dataclass


@dataclass
class MemberDiff:
    player_id: str
    old_data: Optional[dict]
    new_data: Optional[dict]
    change_type: str


def compute_alliance_diff(
    db_members: list[dict],
    api_members: list[dict],
    db_alliance_id: int
) -> dict:
    db_members_map = {m["player_id"]: m for m in db_members}
    api_members_map = {m["player_id"]: m for m in api_members}
    
    added = []
    removed = []
    rank_changed = []
    moved = []
    unchanged = []
    invalid = []
    
    for player_id, api_member in api_members_map.items():
        if not api_member.get("player_id"):
            invalid.append({
                "player_id": player_id,
                "reason": "Missing player_id"
            })
            continue
        
        if player_id not in db_members_map:
            added.append({
                "player_id": api_member["player_id"],
                "rank": api_member.get("rank", "R1"),
                "alliance_tag": api_member.get("alliance_tag", ""),
            })
        else:
            db_member = db_members_map[player_id]
            
            if db_member.get("alliance_id") != db_alliance_id:
                moved.append({
                    "player_id": player_id,
                    "old_alliance_id": db_member.get("alliance_id"),
                    "new_alliance_id": db_alliance_id,
                    "old_rank": db_member.get("alliance_rank", "R1"),
                    "new_rank": api_member.get("rank", "R1"),
                })
            elif db_member.get("alliance_rank") != api_member.get("rank"):
                rank_changed.append({
                    "player_id": player_id,
                    "old_rank": db_member.get("alliance_rank", "R1"),
                    "new_rank": api_member.get("rank", "R1"),
                })
            else:
                unchanged.append({
                    "player_id": player_id,
                    "rank": api_member.get("rank", "R1"),
                })
    
    for player_id, db_member in db_members_map.items():
        if player_id not in api_members_map:
            removed.append({
                "player_id": player_id,
                "old_rank": db_member.get("alliance_rank", "R1"),
                "old_alliance_id": db_member.get("alliance_id"),
            })
    
    return {
        "added": added,
        "removed": removed,
        "rank_changed": rank_changed,
        "moved": moved,
        "unchanged": unchanged,
        "invalid": invalid,
        "summary": {
            "total_added": len(added),
            "total_removed": len(removed),
            "total_rank_changed": len(rank_changed),
            "total_moved": len(moved),
            "total_unchanged": len(unchanged),
            "total_invalid": len(invalid),
        }
    }


def has_changes(diff_result: dict) -> bool:
    summary = diff_result.get("summary", {})
    return (
        summary.get("total_added", 0) > 0 or
        summary.get("total_removed", 0) > 0 or
        summary.get("total_rank_changed", 0) > 0 or
        summary.get("total_moved", 0) > 0
    )
