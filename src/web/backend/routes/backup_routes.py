from fastapi import APIRouter, HTTPException, Request
from typing import Optional

from ..dependencies import require_auth, require_permission, require_role, log_web_action

router = APIRouter(prefix="/api/v1/backups", tags=["backups"])


@router.get("")
async def list_backups(request: Request, limit: int = 20):
    require_auth(request)
    require_permission(request, "WEB_BACKUP_VIEW")
    
    from src.services.backup_service import list_backups
    
    backups = list_backups(limit=limit)
    return {"backups": backups}


@router.post("/create")
async def create_backup(request: Request):
    require_auth(request)
    require_permission(request, "WEB_BACKUP_CREATE")
    
    log_web_action(request, "BACKUP_CREATE", risk_level="MEDIUM")
    
    from src.services.backup_service import create_backup
    result = await create_backup()
    
    return result


@router.post("/{backup_id}/rollback")
async def rollback_backup(request: Request, backup_id: str):
    require_role(request, "ADMIN")
    
    log_web_action(request, "BACKUP_ROLLBACK", backup_id, risk_level="HIGH")
    
    from src.services.rollback_service import rollback_to_backup
    
    result = await rollback_to_backup(backup_id)
    return result
