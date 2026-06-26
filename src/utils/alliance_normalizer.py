import re
from typing import Optional


VALID_RANKS = ["R1", "R2", "R3", "R4", "R5"]


def normalize_player_id(player_id: str) -> Optional[str]:
    if not player_id:
        return None
    
    clean = str(player_id).strip()
    
    if not re.match(r"^\d{6,15}$", clean):
        return None
    
    return clean


def normalize_alliance_tag(tag: str) -> Optional[str]:
    if not tag:
        return None
    
    clean = tag.strip().upper()
    
    if not re.match(r"^[A-Z0-9]{2,10}$", clean):
        return None
    
    return clean


def normalize_alliance_name(name: str) -> Optional[str]:
    if not name:
        return None
    
    clean = name.strip()
    
    if len(clean) < 2 or len(clean) > 100:
        return None
    
    clean = re.sub(r"[^\w\s\-]", "", clean)
    
    return clean if clean else None


def normalize_rank(rank: str) -> str:
    if not rank:
        return "R1"
    
    rank_str = str(rank).strip().upper()
    
    if rank_str in VALID_RANKS:
        return rank_str
    
    rank_match = re.search(r"R?(\d)", rank_str)
    if rank_match:
        num = int(rank_match.group(1))
        if 1 <= num <= 5:
            return f"R{num}"
    
    return "R1"


def normalize_member(member_data: dict) -> Optional[dict]:
    player_id = normalize_player_id(member_data.get("player_id", ""))
    if not player_id:
        return None
    
    alliance_tag = normalize_alliance_tag(member_data.get("alliance_tag", ""))
    alliance_name = normalize_alliance_name(member_data.get("alliance_name", "")) or ""
    rank = normalize_rank(member_data.get("rank", "R1"))
    last_seen = member_data.get("last_seen_at", "")
    
    return {
        "player_id": player_id,
        "alliance_tag": alliance_tag,
        "alliance_name": alliance_name,
        "rank": rank,
        "last_seen_at": last_seen,
    }


def map_external_rank(rank_value: str) -> str:
    if not rank_value:
        return "R1"
    
    rank_str = str(rank_value).upper()
    
    rank_mapping = {
        "LEADER": "R5",
        "CO_LEADER": "R4",
        "OFFICER": "R3",
        "MEMBER": "R2",
        "RECRUIT": "R1",
        "1": "R1", "2": "R2", "3": "R3", "4": "R4", "5": "R5",
    }
    
    return rank_mapping.get(rank_str, normalize_rank(rank_str))
