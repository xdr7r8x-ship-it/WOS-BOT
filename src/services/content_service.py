import logging
from datetime import datetime
from typing import Optional
from database import get_db
from src.i18n import t, DEFAULT_LANGUAGE

logger = logging.getLogger(__name__)


def get_text(guild_id: str, page_key: str, block_key: str, language: str, **kwargs) -> str:
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT custom_text FROM page_content_overrides 
                   WHERE guild_id = ? AND page_key = ? AND block_key = ? AND language = ? AND status = 'ACTIVE'""",
                (guild_id, page_key, block_key, language)
            )
            row = cursor.fetchone()
            if row and row[0]:
                text = row[0]
                if kwargs:
                    try:
                        return text.format(**kwargs)
                    except (KeyError, ValueError):
                        return text
                return text
    except Exception as e:
        logger.warning(f"Error reading content override: {e}")
    
    i18n_key = f"{page_key}.{block_key}"
    return t(i18n_key, language, **kwargs)


def set_text(guild_id: str, page_key: str, block_key: str, language: str, custom_text: str, actor_id: str) -> tuple[bool, str]:
    now = datetime.utcnow().isoformat()
    
    old_text = None
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT custom_text FROM page_content_overrides 
                   WHERE guild_id = ? AND page_key = ? AND block_key = ? AND language = ?""",
                (guild_id, page_key, block_key, language)
            )
            row = cursor.fetchone()
            if row:
                old_text = row[0]
    except Exception:
        pass
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO page_content_overrides 
                   (guild_id, page_key, block_key, language, custom_text, status, updated_by, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, 'ACTIVE', ?, ?, ?)
                   ON CONFLICT(guild_id, page_key, block_key, language) 
                   DO UPDATE SET custom_text = ?, status = 'ACTIVE', updated_by = ?, updated_at = ?""",
                (guild_id, page_key, block_key, language, custom_text, actor_id, now, now, custom_text, actor_id, now)
            )
            
            cursor.execute(
                """INSERT INTO page_content_history 
                   (guild_id, page_key, block_key, language, old_text, new_text, action, changed_by, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, 'UPDATED', ?, ?)""",
                (guild_id, page_key, block_key, language, old_text, custom_text, actor_id, now)
            )
        
        return True, "Text updated successfully"
    except Exception as e:
        logger.error(f"Error saving content override: {e}")
        return False, str(e)


def reset_text(guild_id: str, page_key: str, block_key: str, language: str, actor_id: str) -> tuple[bool, str]:
    now = datetime.utcnow().isoformat()
    
    old_text = None
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT custom_text FROM page_content_overrides 
                   WHERE guild_id = ? AND page_key = ? AND block_key = ? AND language = ?""",
                (guild_id, page_key, block_key, language)
            )
            row = cursor.fetchone()
            if row:
                old_text = row[0]
            
            cursor.execute(
                """UPDATE page_content_overrides SET status = 'DISABLED', updated_at = ?
                   WHERE guild_id = ? AND page_key = ? AND block_key = ? AND language = ?""",
                (now, guild_id, page_key, block_key, language)
            )
            
            cursor.execute(
                """INSERT INTO page_content_history 
                   (guild_id, page_key, block_key, language, old_text, new_text, action, changed_by, created_at)
                   VALUES (?, ?, ?, ?, ?, NULL, 'RESET', ?, ?)""",
                (guild_id, page_key, block_key, language, old_text, actor_id, now)
            )
        
        return True, "Text reset to default"
    except Exception as e:
        logger.error(f"Error resetting content: {e}")
        return False, str(e)


def list_page_blocks(page_key: str, language: str) -> list[dict]:
    from src.i18n import t
    
    blocks = []
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT block_key, default_text, max_length FROM page_content_registry 
                   WHERE page_key = ? AND language = ? AND editable = 1""",
                (page_key, language)
            )
            for row in cursor.fetchall():
                blocks.append({
                    "block_key": row[0],
                    "default_text": row[1],
                    "max_length": row[2],
                    "is_custom": False
                })
    except Exception as e:
        logger.warning(f"Error listing page blocks: {e}")
    
    return blocks


def get_custom_blocks(guild_id: str, page_key: str, language: str) -> dict:
    custom = {}
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT block_key, custom_text FROM page_content_overrides 
                   WHERE guild_id = ? AND page_key = ? AND language = ? AND status = 'ACTIVE'""",
                (guild_id, page_key, language)
            )
            for row in cursor.fetchall():
                custom[row[0]] = row[1]
    except Exception:
        pass
    return custom


def get_effective_page_content(guild_id: str, page_key: str, language: str) -> dict:
    from src.i18n import t
    
    custom = get_custom_blocks(guild_id, page_key, language)
    blocks = list_page_blocks(page_key, language)
    
    result = {}
    for block in blocks:
        key = block["block_key"]
        if key in custom:
            result[key] = {
                "text": custom[key],
                "is_custom": True
            }
        else:
            i18n_key = f"{page_key}.{key}"
            result[key] = {
                "text": t(i18n_key, language),
                "is_custom": False
            }
    
    return result
