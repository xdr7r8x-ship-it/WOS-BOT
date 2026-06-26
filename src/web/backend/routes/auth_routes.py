import httpx
import secrets
from fastapi import APIRouter, HTTPException, Response, Request, Depends, Body
from fastapi.responses import RedirectResponse
from typing import Optional, List
from ..config import config
from ..session import get_session_manager
from ..rbac import has_permission
from ..dependencies import require_auth

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


def get_user_role(user_id: str, guild_id: Optional[str]) -> str:
    from database import get_owner_ids, get_admin_users
    
    if user_id in get_owner_ids():
        return "OWNER"
    
    if guild_id:
        admin_users = get_admin_users(guild_id)
        if user_id in admin_users:
            return "ADMIN"
    
    return "MEMBER"


@router.get("/discord/login")
async def discord_login():
    if not config.DISCORD_OAUTH_CLIENT_ID:
        raise HTTPException(status_code=500, detail="Discord OAuth not configured")
    
    state = secrets.token_urlsafe(16)
    
    params = {
        "client_id": config.DISCORD_OAUTH_CLIENT_ID,
        "redirect_uri": config.DISCORD_OAUTH_REDIRECT_URI,
        "response_type": "code",
        "scope": "identify guilds",
        "state": state,
    }
    
    auth_url = f"https://discord.com/api/oauth2/authorize?" + "&".join(f"{k}={v}" for k, v in params.items())
    return RedirectResponse(url=auth_url)


@router.get("/discord/callback")
async def discord_callback(
    code: str,
    state: Optional[str] = None,
    error: Optional[str] = None
):
    if error:
        raise HTTPException(status_code=400, detail=f"OAuth error: {error}")
    
    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")
    
    token_url = "https://discord.com/api/oauth2/token"
    data = {
        "client_id": config.DISCORD_OAUTH_CLIENT_ID,
        "client_secret": config.DISCORD_OAUTH_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": config.DISCORD_OAUTH_REDIRECT_URI,
    }
    
    async with httpx.AsyncClient() as client:
        try:
            token_response = await client.post(token_url, data=data)
            token_response.raise_for_status()
            token_data = token_response.json()
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to get token: {str(e)}")
        
        access_token = token_data.get("access_token")
        if not access_token:
            raise HTTPException(status_code=400, detail="No access token received")
        
        user_response = await client.get(
            "https://discord.com/api/users/@me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        user_response.raise_for_status()
        user_data = user_response.json()
    
    user_id = user_data.get("id")
    username = user_data.get("username", "")
    
    role = get_user_role(user_id, None)
    
    if role == "MEMBER":
        raise HTTPException(
            status_code=403,
            detail="Access denied. You must be an admin or owner to access the dashboard."
        )
    
    session_manager = get_session_manager()
    session_id = session_manager.create_session(user_id, None, role)
    
    response = Response(content='{"success": true}', media_type="application/json")
    response.set_cookie(
        key=config.WEB_COOKIE_NAME,
        value=session_id,
        httponly=True,
        secure=config.WEB_COOKIE_SECURE,
        samesite="lax",
        max_age=config.WEB_SESSION_TTL_HOURS * 3600,
    )
    
    return response


@router.post("/logout")
async def logout(request: Request):
    session_id = request.cookies.get(config.WEB_COOKIE_NAME)
    if session_id:
        session_manager = get_session_manager()
        session_manager.revoke_session(session_id)
    
    response = Response(content='{"success": true}', media_type="application/json")
    response.delete_cookie(key=config.WEB_COOKIE_NAME)
    return response


@router.get("/me")
async def get_me(request: Request):
    session_id = request.cookies.get(config.WEB_COOKIE_NAME)
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    session_manager = get_session_manager()
    session = session_manager.validate_session(session_id)
    
    if not session:
        raise HTTPException(status_code=401, detail="Session expired or invalid")
    
    from ..rbac import get_role_permissions
    permissions = list(get_role_permissions(session["role_level"]))
    
    return {
        "user_id": session["user_id"],
        "role": session["role_level"],
        "permissions": permissions,
        "guild_id": session.get("guild_id"),
    }


@router.get("/guilds")
async def get_user_guilds(request: Request):
    require_auth(request)
    
    from database import get_owner_ids, get_admin_guild_ids
    
    user_id = request.state.user_id
    role = request.state.role
    
    if role == "OWNER":
        from database import get_all_guild_ids
        guild_ids = get_all_guild_ids()
    else:
        guild_ids = get_admin_guild_ids(user_id)
    
    return {"guilds": guild_ids}


@router.put("/guild")
async def set_user_guild(request: Request, body: dict = Body(...)):
    require_auth(request)
    
    guild_id = body.get("guild_id")
    if not guild_id:
        raise HTTPException(status_code=400, detail="guild_id is required")
    
    user_id = request.state.user_id
    role = request.state.role
    
    if role == "OWNER":
        pass
    else:
        from database import get_admin_user_ids
        admin_ids = get_admin_user_ids(guild_id)
        if user_id not in admin_ids:
            raise HTTPException(status_code=403, detail="You do not have permission for this guild")
    
    session_manager = get_session_manager()
    session_id = request.cookies.get(config.WEB_COOKIE_NAME)
    session_hash = session_id[:16] if session_id else None
    
    if session_hash:
        with session_manager._get_connection() as conn:
            conn.execute(
                "UPDATE web_sessions SET guild_id = ? WHERE session_id_hash = ?",
                (guild_id, session_hash)
            )
            conn.commit()
    
    from ..rbac import get_role_permissions
    permissions = list(get_role_permissions(role))
    
    return {
        "success": True,
        "guild_id": guild_id,
        "user_id": user_id,
        "role": role,
        "permissions": permissions,
    }
