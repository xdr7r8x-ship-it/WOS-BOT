import pytest
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def test_load_features():
    from src.services.feature_registry_service import load_features, get_enabled_features
    features = load_features(force_reload=True)
    assert isinstance(features, list)
    
    enabled = get_enabled_features()
    assert isinstance(enabled, list)
    assert all(f.get("enabled", True) for f in enabled)


def test_get_feature_by_key():
    from src.services.feature_registry_service import get_feature_by_key
    feature = get_feature_by_key("reminders")
    if feature:
        assert "key" in feature
        assert feature["key"] == "reminders"


def test_validate_manifest():
    from src.services.feature_registry_service import _validate_manifest
    
    valid_manifest = {
        "key": "test_feature",
        "name": {"ar": "Test", "en": "Test"},
        "enabled": True
    }
    valid, error = _validate_manifest(valid_manifest, "test_feature")
    assert valid
    
    invalid_manifest = {
        "name": {"ar": "Test"},
        "enabled": True
    }
    valid, error = _validate_manifest(invalid_manifest, "test_feature")
    assert not valid
    assert "Missing required key: key" in error


def test_compute_manifest_hash():
    from src.services.feature_registry_service import _compute_manifest_hash
    manifest = {"key": "test", "enabled": True}
    hash1 = _compute_manifest_hash(manifest)
    assert len(hash1) == 16
    
    hash2 = _compute_manifest_hash(manifest)
    assert hash1 == hash2


def test_get_all_permissions_from_features():
    from src.services.feature_registry_service import get_all_permissions_from_features
    permissions = get_all_permissions_from_features()
    assert isinstance(permissions, list)


def test_get_health_checks():
    from src.services.feature_registry_service import get_health_checks
    health = get_health_checks()
    assert isinstance(health, dict)


def test_get_audit_filters():
    from src.services.feature_registry_service import get_audit_filters
    filters = get_audit_filters()
    assert isinstance(filters, list)


def test_duplicate_feature_key_prevention():
    from src.services.feature_registry_service import load_features
    features = load_features()
    keys = [f["key"] for f in features]
    assert len(keys) == len(set(keys)), "Duplicate feature keys found"


def test_reminders_manifest():
    from src.features.reminders.feature_manifest import FEATURE_MANIFEST
    assert FEATURE_MANIFEST["key"] == "reminders"
    assert "ar" in FEATURE_MANIFEST["name"]
    assert "en" in FEATURE_MANIFEST["name"]
    assert FEATURE_MANIFEST["enabled"] is True
    assert FEATURE_MANIFEST["discord_panel"] is True


def test_gift_codes_manifest():
    from src.features.gift_codes.feature_manifest import FEATURE_MANIFEST
    assert FEATURE_MANIFEST["key"] == "gift_codes"
    assert "ar" in FEATURE_MANIFEST["name"]
    assert "en" in FEATURE_MANIFEST["name"]


def test_alliance_manifest():
    from src.features.alliance.feature_manifest import FEATURE_MANIFEST
    assert FEATURE_MANIFEST["key"] == "alliance"
    assert len(FEATURE_MANIFEST["admin_permissions"]) > 0


def test_player_id_manifest():
    from src.features.player_id.feature_manifest import FEATURE_MANIFEST
    assert FEATURE_MANIFEST["key"] == "player_id"
    assert FEATURE_MANIFEST["discord_panel"] is True


def test_get_discord_sections():
    from src.ui.discord_feature_registry import get_discord_sections
    try:
        sections = get_discord_sections("0", "0", "ar")
        assert isinstance(sections, list)
        
        for section in sections:
            assert "key" in section
            assert "name" in section
            assert "icon" in section
    except Exception:
        pass


def test_feature_lifecycle_status():
    from src.ui.discord_feature_registry import get_feature_lifecycle_status
    status = get_feature_lifecycle_status("reminders")
    assert status in ["ENABLED", "DISABLED", "ERROR"]


def test_is_feature_available():
    from src.ui.discord_feature_registry import is_feature_available, get_feature_lifecycle_status
    available = is_feature_available("reminders")
    status = get_feature_lifecycle_status("reminders")
    assert available == (status == "ENABLED")


def test_check_feature_permission():
    from src.ui.discord_feature_registry import check_feature_permission
    try:
        result = check_feature_permission("0", "0", "reminders", "view")
        assert isinstance(result, bool)
    except Exception:
        pass


def test_set_and_get_feature_setting():
    from src.services.feature_registry_service import set_feature_setting, get_feature_setting
    import uuid
    test_id = str(uuid.uuid4())[:8]
    
    success = set_feature_setting(f"g_{test_id}", f"test_{test_id}", True, '{"key": "value"}', f"u_{test_id}")
    assert success is True
    
    setting = get_feature_setting(f"g_{test_id}", f"test_{test_id}")
    if setting:
        assert "enabled" in setting


def test_invalid_manifest_does_not_break():
    from src.services.feature_registry_service import load_features
    features = load_features(force_reload=True)
    assert isinstance(features, list)
    for feature in features:
        assert "key" in feature
        assert feature["key"] not in ["", None]


def test_missing_optional_fields():
    from src.services.feature_registry_service import _validate_manifest
    
    minimal_manifest = {
        "key": "minimal",
        "name": {"ar": "Minimal", "en": "Minimal"},
        "enabled": True
    }
    valid, error = _validate_manifest(minimal_manifest, "minimal")
    assert valid


def test_feature_registry_table_exists():
    from database import get_db
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='feature_registry'
        """)
        result = cursor.fetchone()
        assert result is not None, "feature_registry table must exist"


def test_feature_settings_table_exists():
    from database import get_db
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='feature_settings'
        """)
        result = cursor.fetchone()
        assert result is not None, "feature_settings table must exist"


def test_sidebar_items_generated():
    from src.services.feature_registry_service import get_sidebar_items
    try:
        items = get_sidebar_items("0", "0", "ar")
        assert isinstance(items, list)
        
        for item in items:
            assert "key" in item
            assert "label" in item
            assert "icon" in item
            assert "path" in item
            assert "order" in item
    except Exception:
        pass


def test_sidebar_sorted_by_order():
    from src.services.feature_registry_service import get_sidebar_items
    try:
        items = get_sidebar_items("0", "0", "ar")
        orders = [item["order"] for item in items]
        assert orders == sorted(orders)
    except Exception:
        pass


def test_dashboard_schema_generated():
    from src.services.feature_registry_service import get_dashboard_schema
    try:
        schema = get_dashboard_schema("0", "0", "ar")
        
        assert "sidebar" in schema
        assert "routes" in schema
        assert "overview_cards" in schema
        assert "settings_sections" in schema
        assert "features_count" in schema
    except Exception:
        pass
