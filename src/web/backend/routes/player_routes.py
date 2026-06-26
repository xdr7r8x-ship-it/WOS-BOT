from fastapi import APIRouter, HTTPException, Request
from typing import Optional, List

from ..dependencies import require_auth, require_permission, log_web_action

router = APIRouter(prefix="/api/v1/players", tags=["players"])


@router.get("")
async def list_players(
    request: Request,
    search: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    require_auth(request)
    require_permission(request, "WEB_PLAYERS_VIEW")
    
    from database import get_active_players, get_disabled_players
    
    players = get_active_players()
    
    if status == "disabled":
        players = get_disabled_players()
    
    if search:
        search_lower = search.lower()
        players = [
            p for p in players
            if search_lower in str(p.get("player_id", "")).lower()
            or search_lower in p.get("nickname", "").lower()
        ]
    
    return {"players": players[offset:offset+limit], "total": len(players)}


@router.get("/stats")
async def get_player_stats(request: Request):
    require_auth(request)
    require_permission(request, "WEB_PLAYERS_VIEW")
    
    from database import get_player_count, get_active_players, get_disabled_players
    
    return {
        "total": get_player_count(),
        "active": len(get_active_players()),
        "disabled": len(get_disabled_players()),
    }


@router.post("/{player_id}/disable")
async def disable_player(request: Request, player_id: str):
    require_auth(request)
    require_permission(request, "WEB_PLAYERS_MANAGE")
    
    log_web_action(request, "PLAYER_DISABLE", player_id, risk_level="MEDIUM")
    
    from database import disable_player as db_disable_player
    
    success = db_disable_player(player_id)
    if not success:
        raise HTTPException(status_code=404, detail="Player not found")
    
    return {"success": True}


@router.post("/{player_id}/enable")
async def enable_player(request: Request, player_id: str):
    require_auth(request)
    require_permission(request, "WEB_PLAYERS_MANAGE")
    
    log_web_action(request, "PLAYER_ENABLE", player_id, risk_level="MEDIUM")
    
    from database import enable_player
    
    success = enable_player(player_id)
    if not success:
        raise HTTPException(status_code=404, detail="Player not found")
    
    return {"success": True}
