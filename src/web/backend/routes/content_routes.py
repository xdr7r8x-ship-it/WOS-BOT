from fastapi import APIRouter, HTTPException, Request
from typing import Optional

from ..dependencies import require_auth, require_permission, log_web_action

router = APIRouter(prefix="/api/v1/content", tags=["content"])


@router.get("/pages")
async def list_pages(request: Request):
    require_auth(request)
    require_permission(request, "WEB_CONTENT_VIEW")
    
    from src.services.content_service import get_pages
    
    pages = get_pages()
    return {"pages": pages}


@router.get("/{page_key}")
async def get_page(request: Request, page_key: str, language: str = "ar"):
    require_auth(request)
    require_permission(request, "WEB_CONTENT_VIEW")
    
    from src.services.content_service import get_page_content
    
    content = get_page_content(page_key, language)
    if not content:
        raise HTTPException(status_code=404, detail="Page not found")
    
    return {"page_key": page_key, "content": content}


@router.patch("/{page_key}/{block_key}")
async def update_block(
    request: Request,
    page_key: str,
    block_key: str,
    value: str,
    language: str = "ar"
):
    require_auth(request)
    require_permission(request, "WEB_CONTENT_EDIT")
    
    log_web_action(request, "CONTENT_UPDATE", f"{page_key}/{block_key}", risk_level="MEDIUM")
    
    from src.services.content_service import update_block_content
    
    success = update_block_content(page_key, block_key, value, language)
    return {"success": success}


@router.post("/{page_key}/{block_key}/reset")
async def reset_block(request: Request, page_key: str, block_key: str):
    require_auth(request)
    require_permission(request, "WEB_CONTENT_EDIT")
    
    log_web_action(request, "CONTENT_RESET", f"{page_key}/{block_key}", risk_level="LOW")
    
    from src.services.content_service import reset_block_default
    
    success = reset_block_default(page_key, block_key)
    return {"success": success}


@router.get("/history")
async def get_content_history(request: Request, page_key: Optional[str] = None):
    require_auth(request)
    require_permission(request, "WEB_CONTENT_VIEW")
    
    from src.services.content_audit_service import get_content_history
    
    history = get_content_history(page_key)
    return {"history": history}
