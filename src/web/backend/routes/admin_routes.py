from fastapi import APIRouter, HTTPException, Request
from typing import Optional, List

from ..dependencies import require_auth, require_permission, require_role, log_web_action

router = APIRouter(prefix="/api/v1/admins", tags=["admins"])


@router.get("")
async def list_admins(request: Request):
    require_auth(request)
    require_permission(request, "WEB_ADMINS_VIEW")
    
    from database import get_admin_users
    
    admins = get_admin_users("0")
    return {"admins": [{"user_id": uid, "role": "ADMIN"} for uid in admins]}


@router.post("")
async def add_admin(request: Request, user_id: str):
    require_role(request, "ADMIN")
    
    if user_id in ["0"]:
        raise HTTPException(status_code=400, detail="Cannot modify owner")
    
    log_web_action(request, "ADMIN_ADD", user_id, risk_level="HIGH")
    
    from database import add_admin_user
    
    success = add_admin_user("0", user_id)
    return {"success": success}


@router.patch("/{user_id}/permissions")
async def update_admin_permissions(request: Request, user_id: str, permissions: List[str]):
    require_role(request, "ADMIN")
    
    if user_id == "0":
        raise HTTPException(status_code=400, detail="Cannot modify owner")
    
    log_web_action(request, "ADMIN_PERMISSIONS_UPDATE", user_id, risk_level="HIGH")
    
    from database import set_admin_permissions
    
    success = set_admin_permissions("0", user_id, permissions)
    return {"success": success}


@router.delete("/{user_id}")
async def remove_admin(request: Request, user_id: str):
    require_role(request, "ADMIN")
    
    if user_id == "0":
        raise HTTPException(status_code=400, detail="Cannot modify owner")
    
    log_web_action(request, "ADMIN_REMOVE", user_id, risk_level="HIGH")
    
    from database import remove_admin_user
    
    success = remove_admin_user("0", user_id)
    return {"success": success}


@router.get("/supervisors")
async def list_supervisors(request: Request):
    require_auth(request)
    require_permission(request, "WEB_ADMINS_VIEW")
    
    from database import get_supervisor_users
    
    supervisors = get_supervisor_users("0")
    return {"supervisors": [{"user_id": uid, "role": "SUPERVISOR"} for uid in supervisors]}


@router.post("/supervisors")
async def add_supervisor(request: Request, user_id: str):
    require_role(request, "ADMIN")
    
    log_web_action(request, "SUPERVISOR_ADD", user_id, risk_level="MEDIUM")
    
    from database import add_supervisor_user
    
    success = add_supervisor_user("0", user_id)
    return {"success": success}


@router.patch("/supervisors/{user_id}/permissions")
async def update_supervisor_permissions(request: Request, user_id: str, permissions: List[str]):
    require_role(request, "ADMIN")
    
    log_web_action(request, "SUPERVISOR_PERMISSIONS_UPDATE", user_id, risk_level="MEDIUM")
    
    from database import set_supervisor_permissions
    
    success = set_supervisor_permissions("0", user_id, permissions)
    return {"success": success}


@router.delete("/supervisors/{user_id}")
async def remove_supervisor(request: Request, user_id: str):
    require_role(request, "ADMIN")
    
    log_web_action(request, "SUPERVISOR_REMOVE", user_id, risk_level="MEDIUM")
    
    from database import remove_supervisor_user
    
    success = remove_supervisor_user("0", user_id)
    return {"success": success}
