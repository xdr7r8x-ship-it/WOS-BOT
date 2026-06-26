import logging
from datetime import datetime
from typing import Optional
from database import get_db

logger = logging.getLogger(__name__)


def save_content_audit(
    guild_id: str,
    actor_id: str,
    action: str,
    page_key: str,
    block_key: str,
    language: str,
    result: str,
    risk_level: str,
    metadata: str = None
):
    now = datetime.utcnow().isoformat()
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO audit_logs 
                   (guild_id, actor_id, action, target, result, risk_level, metadata, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (guild_id, actor_id, action, f"{page_key}:{block_key}:{language}", result, risk_level, metadata, now)
            )
    except Exception as e:
        logger.warning(f"Error saving content audit: {e}")


def get_content_history(
    guild_id: str,
    page_key: str = None,
    block_key: str = None,
    language: str = None,
    limit: int = 50
) -> list[dict]:
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM page_content_history WHERE guild_id = ?"
            params = [guild_id]
            
            if page_key:
                query += " AND page_key = ?"
                params.append(page_key)
            
            if block_key:
                query += " AND block_key = ?"
                params.append(block_key)
            
            if language:
                query += " AND language = ?"
                params.append(language)
            
            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        logger.warning(f"Error getting content history: {e}")
        return []
