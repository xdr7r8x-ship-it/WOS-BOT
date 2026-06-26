import logging
from datetime import datetime
from typing import Optional
from database import get_db
from src.i18n import validate_language, DEFAULT_LANGUAGE

logger = logging.getLogger(__name__)

_language_cache = {}


def get_user_language(guild_id: str, user_id: str) -> str:
    cache_key = f"{guild_id}:{user_id}"
    
    if cache_key in _language_cache:
        return _language_cache[cache_key]
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT language FROM user_language_preferences WHERE guild_id = ? AND user_id = ?",
                (guild_id, user_id)
            )
            row = cursor.fetchone()
            if row:
                lang = validate_language(row[0])
                _language_cache[cache_key] = lang
                return lang
    except Exception as e:
        logger.warning(f"Error reading user language: {e}")
    
    return DEFAULT_LANGUAGE


def set_user_language(guild_id: str, user_id: str, language: str) -> bool:
    cache_key = f"{guild_id}:{user_id}"
    lang = validate_language(language)
    now = datetime.utcnow().isoformat()
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO user_language_preferences (guild_id, user_id, language, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?)
                   ON CONFLICT(guild_id, user_id) 
                   DO UPDATE SET language = ?, updated_at = ?""",
                (guild_id, user_id, lang, now, now, lang, now)
            )
        
        _language_cache[cache_key] = lang
        return True
    except Exception as e:
        logger.error(f"Error saving user language: {e}")
        return False


def get_default_language() -> str:
    return DEFAULT_LANGUAGE


def clear_cache():
    global _language_cache
    _language_cache = {}


def invalidate_cache(guild_id: str = None, user_id: str = None):
    global _language_cache
    if guild_id and user_id:
        cache_key = f"{guild_id}:{user_id}"
        if cache_key in _language_cache:
            del _language_cache[cache_key]
    else:
        _language_cache = {}
