from fastapi import HTTPException, Request
from typing import List
from .session import get_session_manager
from .rbac import has_permission, get_role_permissions
from .config import config


def require_auth(request: Request):
    session_id = request.cookies.get(config.WEB_COOKIE_NAME)
    if not session_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    session_manager = get_session_manager()
    session = session_manager.validate_session(session_id)
    
    if not session:
        raise HTTPException(status_code=401, detail="Session expired or invalid")
    
    request.state.session = session
    request.state.user_id = session["user_id"]
    request.state.role = session["role_level"]
    request.state.guild_id = session.get("guild_id")


def require_permission(request: Request, permission: str):
    role = getattr(request.state, "role", None)
    if not role:
        require_auth(request)
        role = request.state.role
    
    if not has_permission(role, permission):
        raise HTTPException(
            status_code=403,
            detail=f"Permission denied: {permission}"
        )


def require_any_permission(request: Request, permissions: List[str]):
    role = getattr(request.state, "role", None)
    if not role:
        require_auth(request)
        role = request.state.role
    
    for perm in permissions:
        if has_permission(role, perm):
            return
    
    raise HTTPException(
        status_code=403,
        detail="Permission denied"
    )


def require_role(request: Request, min_role: str):
    role = getattr(request.state, "role", None)
    if not role:
        require_auth(request)
        role = request.state.role
    
    role_levels = {"MEMBER": 0, "SUPERVISOR": 1, "ADMIN": 2, "OWNER": 3}
    
    if role_levels.get(role, 0) < role_levels.get(min_role, 0):
        raise HTTPException(
            status_code=403,
            detail=f"Access denied. Minimum role required: {min_role}"
        )


def log_web_action(
    request: Request,
    action: str,
    target: str = None,
    result: str = "success",
    risk_level: str = "LOW",
    metadata: dict = None
):
    if not config.WEB_AUDIT_ENABLED:
        return
    
    from .session import get_session_manager
    from ..security import hash_sensitive
    import hashlib
    
    user_id = getattr(request.state, "user_id", "anonymous")
    guild_id = getattr(request.state, "guild_id", None)
    
    ip_hash = None
    if request.client:
        ip_hash = hash_sensitive(request.client.host)
    
    user_agent = request.headers.get("user-agent", "")
    user_agent_hash = hashlib.sha256(user_agent.encode()).hexdigest()[:16] if user_agent else None
    
    from database import get_db
    import json
    from datetime import datetime
    
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO web_audit_logs 
            (guild_id, actor_id, action, target, result, risk_level, ip_hash, user_agent_hash, metadata, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                guild_id,
                user_id,
                action,
                target,
                result,
                risk_level,
                ip_hash,
                user_agent_hash,
                json.dumps(metadata) if metadata else None,
                datetime.utcnow().isoformat()
            )
        )
        conn.commit()
