from fastapi import APIRouter, Request

from ..dependencies import require_auth, require_permission, log_web_action

router = APIRouter(prefix="/api/v1/alliance-api", tags=["alliance-api"])


@router.get("/health")
async def get_alliance_api_health(request: Request):
    require_auth(request)
    require_permission(request, "WEB_ALLIANCE_API_MANAGE")
    
    from src.api.alliance_client import get_alliance_client
    
    client = get_alliance_client()
    if not client:
        return {"status": "not_configured", "healthy": False}
    
    return await client.health_check()


@router.post("/sync")
async def sync_alliance(request: Request):
    require_auth(request)
    require_permission(request, "WEB_ALLIANCE_API_MANAGE")
    
    log_web_action(request, "ALLIANCE_API_SYNC", risk_level="MEDIUM")
    
    from src.services.alliance_sync_service import sync_alliance_data
    
    result = await sync_alliance_data()
    return result


@router.get("/sync-runs")
async def get_sync_runs(request: Request, limit: int = 20):
    require_auth(request)
    require_permission(request, "WEB_ALLIANCE_API_MANAGE")
    
    from src.services.alliance_sync_service import get_sync_history
    
    history = get_sync_history(limit=limit)
    return {"runs": history}


@router.get("/rank-history")
async def get_rank_history(request: Request, limit: int = 50):
    require_auth(request)
    require_permission(request, "WEB_ALLIANCE_API_MANAGE")
    
    from src.services.alliance_sync_service import get_rank_history
    
    history = get_rank_history(limit=limit)
    return {"history": history}


@router.get("/member-history")
async def get_member_history(request: Request, limit: int = 50):
    require_auth(request)
    require_permission(request, "WEB_ALLIANCE_API_MANAGE")
    
    from src.services.alliance_sync_service import get_member_history
    
    history = get_member_history(limit=limit)
    return {"history": history}
