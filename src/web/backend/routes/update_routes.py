from fastapi import APIRouter, Request

from ..dependencies import require_auth, require_permission, require_role, log_web_action

router = APIRouter(prefix="/api/v1/updates", tags=["updates"])


@router.get("/check")
async def check_updates(request: Request):
    require_auth(request)
    require_permission(request, "WEB_UPDATES_VIEW")
    
    from src.services.update_service import check_for_updates
    result = await check_for_updates()
    return result


@router.get("/plan")
async def get_update_plan(request: Request):
    require_auth(request)
    require_permission(request, "WEB_UPDATES_VIEW")
    
    from src.services.update_service import get_update_plan
    result = await get_update_plan()
    return result


@router.post("/apply")
async def apply_update(request: Request):
    require_role(request, "ADMIN")
    
    log_web_action(request, "UPDATE_APPLY", risk_level="HIGH")
    
    from src.services.update_service import apply_update
    result = await apply_update()
    return result
