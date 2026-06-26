import logging
from typing import List, Dict, Optional, Callable
from src.services.feature_registry_service import get_discord_features_for_user, load_features
from src.services.admin_access_service import check_permission as admin_check_permission

logger = logging.getLogger(__name__)


def check_permission(guild_id: str, user_id: str, permission: str) -> bool:
    return admin_check_permission(guild_id, user_id, permission)

_discord_section_renderers: Dict[str, Callable] = {}
_discord_feature_handlers: Dict[str, Callable] = {}


def register_discord_renderer(feature_key: str, renderer: Callable):
    _discord_section_renderers[feature_key] = renderer
    logger.info(f"Registered Discord renderer for feature: {feature_key}")


def register_discord_handler(feature_key: str, handler: Callable):
    _discord_feature_handlers[feature_key] = handler
    logger.info(f"Registered Discord handler for feature: {feature_key}")


def get_discord_sections(guild_id: str, user_id: str, language: str = "ar") -> List[Dict]:
    features = get_discord_features_for_user(guild_id, user_id)
    sections = []
    
    for feature in features:
        section = {
            "key": feature["key"],
            "name": feature.get("name", {}).get(language, feature["key"]),
            "description": feature.get("description", {}).get(language, ""),
            "icon": feature.get("icon", "📦"),
            "order": _get_feature_order(feature["key"]),
            "has_renderer": feature["key"] in _discord_section_renderers,
        }
        sections.append(section)
    
    sections.sort(key=lambda x: x["order"])
    return sections


def get_discord_feature_handler(feature_key: str) -> Optional[Callable]:
    return _discord_feature_handlers.get(feature_key)


def _get_feature_order(feature_key: str) -> int:
    order_map = {
        "gift_codes": 10,
        "players": 20,
        "player_id": 30,
        "alliance": 40,
        "security": 50,
        "autopilot": 60,
        "reminders": 70,
        "page_content": 80,
    }
    return order_map.get(feature_key, 50)


def render_feature_section(feature_key: str, guild_id: str, user_id: str, language: str) -> Optional[Dict]:
    renderer = _discord_section_renderers.get(feature_key)
    if not renderer:
        return None
    
    try:
        return renderer(guild_id, user_id, language)
    except Exception as e:
        logger.error(f"Error rendering feature {feature_key}: {e}")
        return None


def check_feature_permission(guild_id: str, user_id: str, feature_key: str, action: str = "view") -> bool:
    from src.utils.rbac import check_permission
    
    feature = None
    for f in load_features():
        if f["key"] == feature_key:
            feature = f
            break
    
    if not feature:
        return False
    
    required_perms = feature.get("required_permissions", [])
    admin_perms = feature.get("admin_permissions", [])
    
    if action == "view":
        if not required_perms:
            return True
        for perm in required_perms:
            if check_permission(guild_id, user_id, perm):
                return True
    
    if action == "admin":
        if not admin_perms:
            return True
        for perm in admin_perms:
            if check_permission(guild_id, user_id, perm):
                return True
    
    return False


def get_feature_lifecycle_status(feature_key: str) -> str:
    from src.services.feature_registry_service import get_feature_by_key
    
    feature = get_feature_by_key(feature_key)
    if not feature:
        return "ERROR"
    
    if not feature.get("enabled", True):
        return "DISABLED"
    
    return "ENABLED"


def is_feature_available(feature_key: str) -> bool:
    status = get_feature_lifecycle_status(feature_key)
    return status == "ENABLED"


def get_all_discord_features_status() -> Dict[str, str]:
    features = load_features()
    status = {}
    
    for feature in features:
        if feature.get("discord_panel", False):
            status[feature["key"]] = get_feature_lifecycle_status(feature["key"])
    
    return status
