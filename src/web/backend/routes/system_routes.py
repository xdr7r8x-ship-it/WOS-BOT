from fastapi import APIRouter, Request

from ..dependencies import require_auth, require_permission

router = APIRouter(prefix="/api/v1/system", tags=["system"])


@router.get("/status")
async def get_system_status(request: Request):
    require_auth(request)
    require_permission(request, "WEB_SYSTEM_VIEW")
    
    from src.services.monitor_service import get_system_status
    return get_system_status()


@router.get("/diagnostics")
async def get_diagnostics(request: Request):
    require_auth(request)
    require_permission(request, "WEB_SYSTEM_VIEW")
    
    from src.services.diagnostics_service import get_diagnostics
    return get_diagnostics()


@router.get("/autopilot")
async def get_autopilot_status(request: Request):
    require_auth(request)
    require_permission(request, "WEB_SYSTEM_VIEW")
    
    from src.services.autopilot_service import get_autopilot_status
    return get_autopilot_status()


@router.get("/watchdog")
async def get_watchdog_status(request: Request):
    require_auth(request)
    require_permission(request, "WEB_SYSTEM_VIEW")
    
    from src.services.watchdog_service import get_watchdog_status
    return get_watchdog_status()


@router.get("/predict")
async def get_predictions(request: Request):
    require_auth(request)
    require_permission(request, "WEB_SYSTEM_VIEW")
    
    from src.services.predictive_service import get_predictions
    return get_predictions()
