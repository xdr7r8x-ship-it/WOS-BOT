import logging
from datetime import datetime
from typing import Optional
from database import get_db

logger = logging.getLogger(__name__)

CONTENT_BLOCKS = {
    "main_panel": {
        "title": {"max_length": 256, "type": "text"},
        "description": {"max_length": 2048, "type": "text"},
        "codes_label": {"max_length": 100, "type": "text"},
        "players_label": {"max_length": 100, "type": "text"},
        "alliances_label": {"max_length": 100, "type": "text"},
        "security_label": {"max_length": 100, "type": "text"},
        "system_label": {"max_length": 100, "type": "text"},
        "backup_label": {"max_length": 100, "type": "text"},
        "updates_label": {"max_length": 100, "type": "text"},
        "maintenance_label": {"max_length": 100, "type": "text"},
        "health_label": {"max_length": 100, "type": "text"},
    },
    "codes_view": {
        "title": {"max_length": 256, "type": "text"},
        "description": {"max_length": 2048, "type": "text"},
        "redeem_label": {"max_length": 100, "type": "text"},
        "status_label": {"max_length": 100, "type": "text"},
        "queue_label": {"max_length": 100, "type": "text"},
    },
    "players_view": {
        "title": {"max_length": 256, "type": "text"},
        "description": {"max_length": 2048, "type": "text"},
        "list_label": {"max_length": 100, "type": "text"},
        "remove_label": {"max_length": 100, "type": "text"},
    },
    "security_view": {
        "title": {"max_length": 256, "type": "text"},
        "description": {"max_length": 2048, "type": "text"},
        "scan_label": {"max_length": 100, "type": "text"},
        "audit_label": {"max_length": 100, "type": "text"},
        "incidents_label": {"max_length": 100, "type": "text"},
        "blocked_label": {"max_length": 100, "type": "text"},
    },
    "system_view": {
        "title": {"max_length": 256, "type": "text"},
        "description": {"max_length": 2048, "type": "text"},
        "info_label": {"max_length": 100, "type": "text"},
        "diagnostics_label": {"max_length": 100, "type": "text"},
        "integrity_label": {"max_length": 100, "type": "text"},
    },
    "backup_view": {
        "title": {"max_length": 256, "type": "text"},
        "description": {"max_length": 2048, "type": "text"},
        "create_label": {"max_length": 100, "type": "text"},
        "list_label": {"max_length": 100, "type": "text"},
        "rollback_label": {"max_length": 100, "type": "text"},
    },
    "updates_view": {
        "title": {"max_length": 256, "type": "text"},
        "description": {"max_length": 2048, "type": "text"},
        "check_label": {"max_length": 100, "type": "text"},
        "plan_label": {"max_length": 100, "type": "text"},
        "apply_label": {"max_length": 100, "type": "text"},
    },
    "maintenance_view": {
        "title": {"max_length": 256, "type": "text"},
        "description": {"max_length": 2048, "type": "text"},
        "cleanup_label": {"max_length": 100, "type": "text"},
        "retry_label": {"max_length": 100, "type": "text"},
        "logs_label": {"max_length": 100, "type": "text"},
    },
    "health_view": {
        "title": {"max_length": 256, "type": "text"},
        "description": {"max_length": 2048, "type": "text"},
        "status_healthy": {"max_length": 100, "type": "text"},
        "status_degraded": {"max_length": 100, "type": "text"},
        "status_failed": {"max_length": 100, "type": "text"},
    },
    "settings_view": {
        "title": {"max_length": 256, "type": "text"},
        "description": {"max_length": 2048, "type": "text"},
        "owner_label": {"max_length": 100, "type": "text"},
        "admin_label": {"max_length": 100, "type": "text"},
        "supervisor_label": {"max_length": 100, "type": "text"},
    },
    "alliance_view": {
        "title": {"max_length": 256, "type": "text"},
        "description": {"max_length": 2048, "type": "text"},
        "list_label": {"max_length": 100, "type": "text"},
        "add_label": {"max_length": 100, "type": "text"},
        "edit_label": {"max_length": 100, "type": "text"},
        "members_label": {"max_length": 100, "type": "text"},
        "stats_label": {"max_length": 100, "type": "text"},
        "sync_label": {"max_length": 100, "type": "text"},
        "health_label": {"max_length": 100, "type": "text"},
    },
    "language_view": {
        "title": {"max_length": 256, "type": "text"},
        "description": {"max_length": 2048, "type": "text"},
        "arabic_label": {"max_length": 100, "type": "text"},
        "english_label": {"max_length": 100, "type": "text"},
    },
}


def initialize_content_registry():
    from src.i18n import t
    from src.i18n.ar import ARABIC_TRANSLATIONS
    from src.i18n.en import ENGLISH_TRANSLATIONS
    
    now = datetime.utcnow().isoformat()
    
    for page_key, blocks in CONTENT_BLOCKS.items():
        for block_key, config in blocks.items():
            i18n_key = f"{page_key}.{block_key}"
            default_ar = ARABIC_TRANSLATIONS.get(i18n_key, block_key)
            default_en = ENGLISH_TRANSLATIONS.get(i18n_key, block_key)
            
            try:
                with get_db() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        """INSERT OR IGNORE INTO page_content_registry 
                           (page_key, block_key, language, default_text, max_length, editable, content_type, created_at, updated_at)
                           VALUES (?, ?, ?, ?, ?, 1, 'text', ?, ?)""",
                        (page_key, block_key, 'ar', default_ar, config["max_length"], now, now)
                    )
                    cursor.execute(
                        """INSERT OR IGNORE INTO page_content_registry 
                           (page_key, block_key, language, default_text, max_length, editable, content_type, created_at, updated_at)
                           VALUES (?, ?, ?, ?, ?, 1, 'text', ?, ?)""",
                        (page_key, block_key, 'en', default_en, config["max_length"], now, now)
                    )
            except Exception as e:
                logger.warning(f"Error initializing content registry: {e}")


def get_block_max_length(page_key: str, block_key: str, language: str) -> int:
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT max_length FROM page_content_registry 
                   WHERE page_key = ? AND block_key = ? AND language = ?""",
                (page_key, block_key, language)
            )
            row = cursor.fetchone()
            if row:
                return row[0]
    except Exception:
        pass
    
    return CONTENT_BLOCKS.get(page_key, {}).get(block_key, {}).get("max_length", 500)


def get_block_default(page_key: str, block_key: str, language: str) -> str:
    from src.i18n import t
    i18n_key = f"{page_key}.{block_key}"
    return t(i18n_key, language)


def is_block_editable(page_key: str, block_key: str, language: str) -> bool:
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT editable FROM page_content_registry 
                   WHERE page_key = ? AND block_key = ? AND language = ?""",
                (page_key, block_key, language)
            )
            row = cursor.fetchone()
            if row:
                return bool(row[0])
    except Exception:
        pass
    
    return True
