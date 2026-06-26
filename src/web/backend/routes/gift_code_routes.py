from fastapi import APIRouter, HTTPException, Request, Body
from typing import List, Optional
from datetime import datetime

from ..dependencies import require_auth, require_permission, log_web_action

router = APIRouter(prefix="/api/v1/gift-codes", tags=["gift-codes"])


@router.get("")
async def list_gift_codes(
    request: Request,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    require_auth(request)
    require_permission(request, "WEB_GIFT_CODES_VIEW")
    
    from database import get_gift_codes
    codes = get_gift_codes(limit=limit, offset=offset)
    
    if status:
        codes = [c for c in codes if c.get("status") == status]
    
    for code in codes:
        code["code_hash"] = code.get("code_hash", "")[:8] + "***"
    
    return {"codes": codes, "total": len(codes)}


@router.post("/redeem")
async def submit_gift_code(
    request: Request,
    body: dict = Body(...),
    background_tasks=None
):
    require_auth(request)
    require_permission(request, "WEB_GIFT_CODES_MANAGE")
    
    code = body.get("code", "")
    if not code:
        raise HTTPException(status_code=400, detail="Code is required")
    
    log_web_action(request, "GIFT_CODE_SUBMIT", code[:8] + "***", risk_level="MEDIUM")
    
    from src.services.redeem_service import RedeemService
    from database import save_gift_code
    
    guild_id = "web_dashboard"
    code_hash = f"web_{hash(code) % 1000000}"
    
    save_gift_code(guild_id, code_hash, code)
    
    service = RedeemService()
    
    try:
        await service.process_code(guild_id, code)
        return {"status": "success", "message": "Code submitted for processing", "code_hash": code_hash}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.get("/{code_hash}/status")
async def get_code_status(request: Request, code_hash: str):
    require_auth(request)
    require_permission(request, "WEB_GIFT_CODES_VIEW")
    
    from database import get_code_by_hash, get_redemptions_by_code
    
    code = get_code_by_hash(code_hash)
    if not code:
        raise HTTPException(status_code=404, detail="Code not found")
    
    redemptions = get_redemptions_by_code(code_hash)
    
    return {
        "code": {
            "code_hash": code.get("code_hash", "")[:8] + "***",
            "status": code.get("status"),
            "submitted_at": code.get("submitted_at"),
        },
        "redemptions": redemptions
    }


@router.get("/queue")
async def get_queue(request: Request):
    require_auth(request)
    require_permission(request, "WEB_GIFT_CODES_VIEW")
    
    from database import get_queue
    queue = get_queue()
    
    return {"queue": queue}


@router.get("/stats")
async def get_stats(request: Request):
    require_auth(request)
    require_permission(request, "WEB_GIFT_CODES_VIEW")
    
    from database import get_code_stats
    stats = get_code_stats()
    
    return stats
