from fastapi import APIRouter, HTTPException, Request
from typing import Optional, List

from ..dependencies import require_auth, require_permission, log_web_action

router = APIRouter(prefix="/api/v1/alliances", tags=["alliances"])


@router.get("")
async def list_alliances(request: Request):
    require_auth(request)
    require_permission(request, "WEB_ALLIANCE_VIEW")
    
    from src.services.alliance_service import get_alliances
    
    alliances = get_alliances()
    return {"alliances": alliances}


@router.post("")
async def create_alliance(request: Request, name: str, tag: str):
    require_auth(request)
    require_permission(request, "WEB_ALLIANCE_MANAGE")
    
    log_web_action(request, "ALLIANCE_CREATE", name, risk_level="MEDIUM")
    
    from src.services.alliance_service import create_alliance
    
    alliance = create_alliance(name, tag)
    if not alliance:
        raise HTTPException(status_code=400, detail="Failed to create alliance")
    
    return alliance


@router.patch("/{alliance_id}")
async def update_alliance(request: Request, alliance_id: int, name: Optional[str] = None, tag: Optional[str] = None):
    require_auth(request)
    require_permission(request, "WEB_ALLIANCE_MANAGE")
    
    log_web_action(request, "ALLIANCE_UPDATE", str(alliance_id), risk_level="MEDIUM")
    
    from src.services.alliance_service import update_alliance
    
    alliance = update_alliance(alliance_id, name, tag)
    if not alliance:
        raise HTTPException(status_code=404, detail="Alliance not found")
    
    return alliance


@router.post("/{alliance_id}/disable")
async def disable_alliance(request: Request, alliance_id: int):
    require_auth(request)
    require_permission(request, "WEB_ALLIANCE_MANAGE")
    
    log_web_action(request, "ALLIANCE_DISABLE", str(alliance_id), risk_level="MEDIUM")
    
    from src.services.alliance_service import disable_alliance
    
    success = disable_alliance(alliance_id)
    if not success:
        raise HTTPException(status_code=404, detail="Alliance not found")
    
    return {"success": True}


@router.get("/{alliance_id}/members")
async def get_alliance_members(request: Request, alliance_id: int):
    require_auth(request)
    require_permission(request, "WEB_ALLIANCE_VIEW")
    
    from src.services.alliance_member_service import get_members
    
    members = get_members(alliance_id)
    return {"members": members}


@router.post("/member/assign")
async def assign_member(request: Request, player_id: int, alliance_id: int):
    require_auth(request)
    require_permission(request, "WEB_ALLIANCE_MANAGE")
    
    log_web_action(request, "ALLIANCE_MEMBER_ASSIGN", f"player:{player_id}", risk_level="MEDIUM")
    
    from src.services.alliance_member_service import assign_member
    
    success = assign_member(player_id, alliance_id)
    return {"success": success}


@router.post("/member/remove")
async def remove_member(request: Request, player_id: int, alliance_id: int):
    require_auth(request)
    require_permission(request, "WEB_ALLIANCE_MANAGE")
    
    log_web_action(request, "ALLIANCE_MEMBER_REMOVE", f"player:{player_id}", risk_level="MEDIUM")
    
    from src.services.alliance_member_service import remove_member
    
    success = remove_member(player_id, alliance_id)
    return {"success": success}


@router.post("/member/rank")
async def rank_member(request: Request, player_id: int, rank: str):
    require_auth(request)
    require_permission(request, "WEB_ALLIANCE_MANAGE")
    
    log_web_action(request, "ALLIANCE_MEMBER_RANK", f"player:{player_id} rank:{rank}", risk_level="MEDIUM")
    
    from src.services.alliance_member_service import update_rank
    
    success = update_rank(player_id, rank)
    return {"success": success}


@router.get("/stats")
async def get_alliance_stats(request: Request):
    require_auth(request)
    require_permission(request, "WEB_ALLIANCE_VIEW")
    
    from src.services.alliance_service import get_stats
    
    stats = get_stats()
    return stats


@router.get("/audit")
async def get_alliance_audit(request: Request):
    require_auth(request)
    require_permission(request, "WEB_ALLIANCE_VIEW")
    
    from database import get_audit_logs
    
    logs = get_audit_logs(action_like="ALLIANCE%", limit=50)
    return {"logs": logs}
