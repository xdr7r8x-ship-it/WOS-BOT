from fastapi import APIRouter, HTTPException, Request

from ..dependencies import require_auth, require_permission, log_web_action

router = APIRouter(prefix="/api/v1/player-panel", tags=["player-panel"])


@router.get("/status")
async def get_player_panel_status(request: Request):
    require_auth(request)
    require_permission(request, "WEB_PLAYER_PANEL_MANAGE")
    
    from database import get_guild_settings
    
    settings = get_guild_settings("0")
    register_channel = settings.get("register_channel_id", "Not set")
    
    from database import get_player_count
    
    return {
        "enabled": True,
        "register_channel": register_channel,
        "registered_count": get_player_count(),
    }


@router.post("/refresh")
async def refresh_player_panel(request: Request):
    require_auth(request)
    require_permission(request, "WEB_PLAYER_PANEL_MANAGE")
    
    log_web_action(request, "PLAYER_PANEL_REFRESH", risk_level="LOW")
    
    return {"success": True, "message": "Panel refreshed"}


@router.post("/language")
async def set_panel_language(request: Request, language: str):
    require_auth(request)
    require_permission(request, "WEB_PLAYER_PANEL_MANAGE")
    
    if language not in ["ar", "en"]:
        raise HTTPException(status_code=400, detail="Invalid language")
    
    log_web_action(request, "PLAYER_PANEL_LANGUAGE", language, risk_level="LOW")
    
    from database import save_guild_settings, get_guild_settings
    
    settings = get_guild_settings("0")
    settings["language"] = language
    save_guild_settings("0", settings)
    
    return {"success": True, "language": language}
