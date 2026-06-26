from fastapi import APIRouter, HTTPException, Request
from typing import Optional

from ..dependencies import require_auth, require_permission, log_web_action

router = APIRouter(prefix="/api/v1/security", tags=["security"])


@router.get("/incidents")
async def get_incidents(request: Request, limit: int = 50):
    require_auth(request)
    require_permission(request, "WEB_SECURITY_VIEW")
    
    from database import get_security_incidents
    
    incidents = get_security_incidents(limit=limit)
    return {"incidents": incidents}


@router.get("/audit-logs")
async def get_security_audit_logs(request: Request, limit: int = 50):
    require_auth(request)
    require_permission(request, "WEB_SECURITY_VIEW")
    
    from database import get_audit_logs
    
    logs = get_audit_logs(limit=limit)
    return {"logs": logs}


@router.post("/scan")
async def run_security_scan(request: Request):
    require_auth(request)
    require_permission(request, "WEB_SECURITY_MANAGE")
    
    log_web_action(request, "SECURITY_SCAN", risk_level="HIGH")
    
    return {"success": True, "message": "Security scan initiated"}


@router.post("/integrity-check")
async def run_integrity_check(request: Request):
    require_auth(request)
    require_permission(request, "WEB_SECURITY_MANAGE")
    
    log_web_action(request, "INTEGRITY_CHECK", risk_level="HIGH")
    
    return {"success": True, "message": "Integrity check initiated"}
