from fastapi import APIRouter, Request
from typing import Optional

from ..dependencies import require_auth, require_permission

router = APIRouter(prefix="/api/v1/audit", tags=["audit"])


@router.get("/logs")
async def get_audit_logs(
    request: Request,
    actor_id: Optional[str] = None,
    action: Optional[str] = None,
    result: Optional[str] = None,
    risk_level: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    require_auth(request)
    require_permission(request, "WEB_AUDIT_VIEW")
    
    from database import get_audit_logs
    
    logs = get_audit_logs(
        actor_id=actor_id,
        action_like=action,
        result=result,
        risk_level=risk_level,
        limit=limit,
        offset=offset
    )
    
    return {"logs": logs, "total": len(logs)}


@router.get("/web")
async def get_web_audit_logs(
    request: Request,
    actor_id: Optional[str] = None,
    action: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    require_auth(request)
    require_permission(request, "WEB_AUDIT_VIEW")
    
    from database import get_web_audit_logs
    
    logs = get_web_audit_logs(
        actor_id=actor_id,
        action_like=action,
        limit=limit,
        offset=offset
    )
    
    return {"logs": logs, "total": len(logs)}
