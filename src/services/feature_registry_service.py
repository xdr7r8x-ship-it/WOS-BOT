import os
import importlib
import importlib.util
import hashlib
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path
from database import get_db
from src.utils.rbac import ALL_PERMISSIONS
from src.services.admin_access_service import check_permission, get_user_permissions, is_owner

logger = logging.getLogger(__name__)

FEATURES_DIR = Path(__file__).parent.parent / "features"

FEATURE_MANIFEST_KEYS = [
    "key", "name", "description", "icon", "category", "version",
    "enabled", "web_dashboard", "discord_panel", "requires_auth",
    "required_permissions", "admin_permissions", "routes",
    "api_prefix", "health_check", "overview_cards",
    "settings_sections", "audit_events"
]

_cached_features: List[Dict] = []
_last_load_time: Optional[datetime] = None
FEATURE_CACHE_TTL_SECONDS = 300


def _compute_manifest_hash(manifest: Dict) -> str:
    import json
    return hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest()[:16]


def _validate_manifest(manifest: Dict, feature_key: str) -> tuple[bool, str]:
    if not isinstance(manifest, dict):
        return False, "Manifest must be a dictionary"
    
    required_keys = ["key", "name", "enabled"]
    for key in required_keys:
        if key not in manifest:
            return False, f"Missing required key: {key}"
    
    if manifest.get("key") != feature_key:
        return False, f"Feature key mismatch: {manifest.get('key')} != {feature_key}"
    
    if "name" in manifest:
        if not isinstance(manifest["name"], dict):
            return False, "name must be a dict with ar/en keys"
        if "ar" not in manifest["name"] or "en" not in manifest["name"]:
            return False, "name must have ar and en keys"
    
    if "enabled" in manifest and not isinstance(manifest["enabled"], bool):
        return False, "enabled must be a boolean"
    
    if "required_permissions" in manifest:
        for perm in manifest["required_permissions"]:
            if perm not in ALL_PERMISSIONS:
                logger.warning(f"Unknown permission in {feature_key}: {perm}")
    
    if "admin_permissions" in manifest:
        for perm in manifest["admin_permissions"]:
            if perm not in ALL_PERMISSIONS:
                logger.warning(f"Unknown permission in {feature_key}: {perm}")
    
    return True, ""


def _load_feature_manifest(feature_path: Path) -> Optional[Dict]:
    try:
        manifest_file = feature_path / "feature_manifest.py"
        if not manifest_file.exists():
            return None
        
        spec = importlib.util.spec_from_file_location("feature_manifest", manifest_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        manifest = getattr(module, "FEATURE_MANIFEST", None)
        if not manifest:
            return None
        
        feature_key = feature_path.name
        valid, error = _validate_manifest(manifest, feature_key)
        if not valid:
            logger.error(f"Invalid manifest for {feature_key}: {error}")
            return None
        
        manifest["_manifest_path"] = str(manifest_file)
        return manifest
    except Exception as e:
        logger.error(f"Error loading feature manifest from {feature_path}: {e}")
        return None


def load_features(force_reload: bool = False) -> List[Dict]:
    global _cached_features, _last_load_time
    
    now = datetime.utcnow()
    if not force_reload and _cached_features and _last_load_time:
        if (now - _last_load_time).total_seconds() < FEATURE_CACHE_TTL_SECONDS:
            return _cached_features
    
    features = []
    
    if not FEATURES_DIR.exists():
        logger.warning(f"Features directory not found: {FEATURES_DIR}")
        _cached_features = []
        _last_load_time = now
        return []
    
    for item in FEATURES_DIR.iterdir():
        if not item.is_dir():
            continue
        if item.name.startswith("_"):
            continue
        
        manifest = _load_feature_manifest(item)
        if manifest:
            manifest["_loaded_at"] = now.isoformat()
            manifest["_manifest_hash"] = _compute_manifest_hash(manifest)
            features.append(manifest)
    
    _cached_features = features
    _last_load_time = now
    
    _sync_to_database(features)
    
    return features


def _sync_to_database(features: List[Dict]):
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            now = datetime.utcnow().isoformat()
            
            for feature in features:
                cursor.execute("""
                    INSERT INTO feature_registry 
                    (feature_key, feature_name, version, enabled, web_dashboard, discord_panel, 
                     category, manifest_hash, last_loaded_at, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(feature_key) DO UPDATE SET
                        version = excluded.version,
                        enabled = excluded.enabled,
                        web_dashboard = excluded.web_dashboard,
                        discord_panel = excluded.discord_panel,
                        category = excluded.category,
                        manifest_hash = excluded.manifest_hash,
                        last_loaded_at = excluded.last_loaded_at,
                        updated_at = excluded.updated_at
                """, (
                    feature["key"],
                    feature.get("name", {}).get("en", feature["key"]),
                    feature.get("version", "1.0.0"),
                    1 if feature.get("enabled", True) else 0,
                    1 if feature.get("web_dashboard", True) else 0,
                    1 if feature.get("discord_panel", False) else 0,
                    feature.get("category", "general"),
                    feature["_manifest_hash"],
                    now, now, now
                ))
    except Exception as e:
        logger.error(f"Error syncing features to database: {e}")


def get_enabled_features() -> List[Dict]:
    features = load_features()
    return [f for f in features if f.get("enabled", True)]


def get_feature_by_key(feature_key: str) -> Optional[Dict]:
    features = load_features()
    for feature in features:
        if feature["key"] == feature_key:
            return feature
    return None


def get_features_for_user(guild_id: str, user_id: str) -> List[Dict]:
    features = get_enabled_features()
    user_features = []
    
    for feature in features:
        required_perms = feature.get("required_permissions", [])
        
        if not required_perms:
            user_features.append(feature)
            continue
        
        has_access = False
        for perm in required_perms:
            if check_permission(guild_id, user_id, perm):
                has_access = True
                break
        
        if has_access:
            user_features.append(feature)
    
    return user_features


def get_features_for_owner(guild_id: str, user_id: str) -> List[Dict]:
    if is_owner(user_id):
        return get_enabled_features()
    return get_features_for_user(guild_id, user_id)


def get_sidebar_items(guild_id: str, user_id: str, language: str = "ar") -> List[Dict]:
    features = get_features_for_owner(guild_id, user_id)
    sidebar_items = []
    
    for feature in features:
        if not feature.get("web_dashboard", True):
            continue
        
        routes = feature.get("routes", [])
        for route in routes:
            if not route.get("show_in_sidebar", True):
                continue
            
            item = {
                "key": feature["key"],
                "label": route.get("label", feature.get("name", {}).get(language, feature["key"])),
                "icon": feature.get("icon", "📦"),
                "path": route.get("path", f"/{feature['key']}"),
                "order": route.get("order", 50),
                "category": feature.get("category", "general"),
                "permission": route.get("permission"),
            }
            sidebar_items.append(item)
    
    sidebar_items.sort(key=lambda x: x["order"])
    return sidebar_items


def get_dashboard_schema(guild_id: str, user_id: str, language: str = "ar") -> Dict[str, Any]:
    features = get_features_for_owner(guild_id, user_id)
    
    sidebar = get_sidebar_items(guild_id, user_id, language)
    
    routes = []
    for feature in features:
        for route in feature.get("routes", []):
            routes.append({
                "key": feature["key"],
                "path": route.get("path", f"/{feature['key']}"),
                "component": route.get("component", f"{feature['key'].title().replace('_', '')}Page"),
                "permission": route.get("permission"),
            })
    
    overview_cards = []
    for feature in features:
        for card in feature.get("overview_cards", []):
            perm = card.get("permission")
            if perm and not check_permission(guild_id, user_id, perm):
                continue
            overview_cards.append({
                "key": f"{feature['key']}_{card['key']}",
                "feature": feature["key"],
                "label": card.get("label", card.get("label_key", card["key"])),
                "metric_endpoint": card.get("metric_endpoint"),
                "icon": feature.get("icon", "📦"),
            })
    
    settings_sections = []
    for feature in features:
        for section in feature.get("settings_sections", []):
            perm = section.get("permission")
            if perm and not check_permission(guild_id, user_id, perm):
                continue
            settings_sections.append({
                "key": section.get("key", feature["key"]),
                "feature": feature["key"],
                "label": section.get("label", section.get("label_key", feature["key"])),
                "icon": feature.get("icon", "📦"),
            })
    
    return {
        "sidebar": sidebar,
        "routes": routes,
        "overview_cards": overview_cards,
        "settings_sections": settings_sections,
        "features_count": len(features),
    }


def get_all_permissions_from_features() -> List[str]:
    features = get_enabled_features()
    permissions = set()
    
    for feature in features:
        for perm in feature.get("required_permissions", []):
            permissions.add(perm)
        for perm in feature.get("admin_permissions", []):
            permissions.add(perm)
    
    return sorted(list(permissions))


def get_health_checks() -> Dict[str, str]:
    features = get_enabled_features()
    health = {}
    
    for feature in features:
        health_check = feature.get("health_check")
        if health_check:
            health[feature["key"]] = "healthy"
    
    return health


def get_audit_filters() -> List[Dict]:
    features = get_enabled_features()
    filters = []
    
    for feature in features:
        for event in feature.get("audit_events", []):
            filters.append({
                "event": event,
                "feature": feature["key"],
                "label": f"{feature.get('name', {}).get('en', feature['key'])} - {event}",
                "icon": feature.get("icon", "📦"),
            })
    
    return filters


def get_discord_features_for_user(guild_id: str, user_id: str) -> List[Dict]:
    features = get_enabled_features()
    user_features = []
    
    for feature in features:
        if not feature.get("discord_panel", False):
            continue
        
        required_perms = feature.get("required_permissions", [])
        
        if not required_perms:
            user_features.append(feature)
            continue
        
        has_access = False
        for perm in required_perms:
            if check_permission(guild_id, user_id, perm):
                has_access = True
                break
        
        if has_access:
            user_features.append(feature)
    
    return user_features


def set_feature_setting(guild_id: str, feature_key: str, enabled: bool, settings_json: str, updated_by: str) -> bool:
    try:
        now = datetime.utcnow().isoformat()
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO feature_settings 
                (guild_id, feature_key, enabled, settings_json, updated_by, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(guild_id, feature_key) DO UPDATE SET
                    enabled = excluded.enabled,
                    settings_json = COALESCE(excluded.settings_json, settings_json),
                    updated_by = excluded.updated_by,
                    updated_at = excluded.updated_at
            """, (guild_id, feature_key, 1 if enabled else 0, settings_json, updated_by, now, now))
        return True
    except Exception as e:
        logger.error(f"Error setting feature: {e}")
        return False


def get_feature_setting(guild_id: str, feature_key: str) -> Optional[Dict]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT enabled, settings_json, updated_by, updated_at
            FROM feature_settings WHERE guild_id = ? AND feature_key = ?
        """, (guild_id, feature_key))
        row = cursor.fetchone()
        if row:
            return {
                "enabled": bool(row[0]),
                "settings_json": row[1],
                "updated_by": row[2],
                "updated_at": row[3],
            }
    return None
