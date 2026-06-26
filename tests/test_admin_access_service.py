import pytest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

os.environ["BOT_OWNER_IDS"] = "111111,222222"

from src.services.admin_access_service import (
    get_owner_ids, is_owner, get_role_level,
    is_authorized, check_permission,
    validate_owner_ids_config
)
from src.utils.rbac import (
    ALL_PERMISSIONS, ADMIN_DEFAULT_PERMISSIONS,
    SUPERVISOR_DEFAULT_PERMISSIONS, ROLE_LEVELS
)


class TestOwnerIdentification:
    def test_get_owner_ids(self):
        ids = get_owner_ids()
        assert "111111" in ids
        assert "222222" in ids
        assert len(ids) == 2

    def test_is_owner_true(self):
        assert is_owner("111111") is True
        assert is_owner("222222") is True

    def test_is_owner_false(self):
        assert is_owner("333333") is False

    def test_is_authorized_owner(self):
        assert is_authorized("guild1", "111111") is True


class TestRBACValidation:
    def test_validate_owner_ids_config_valid(self):
        valid, msg = validate_owner_ids_config()
        assert valid is True

    def test_validate_owner_ids_config_empty(self):
        os.environ["BOT_OWNER_IDS"] = ""
        from src.services.admin_access_service import validate_owner_ids_config
        valid, msg = validate_owner_ids_config()
        assert valid is False
        assert "not configured" in msg.lower()
        os.environ["BOT_OWNER_IDS"] = "111111,222222"


class TestPermissions:
    def test_owner_has_all_permissions(self):
        assert check_permission("guild", "111111", "BACKUP_CREATE") is True
        assert check_permission("guild", "111111", "ADMINS_CREATE") is True
        assert check_permission("guild", "111111", "ROLLBACK_EXECUTE") is True

    def test_non_admin_no_permissions(self):
        assert check_permission("guild_test5", "666666", "BACKUP_CREATE") is False
        assert check_permission("guild_test5", "666666", "PANEL_VIEW") is False


class TestRoleLevels:
    def test_role_levels_defined(self):
        assert ROLE_LEVELS["OWNER"] == 3
        assert ROLE_LEVELS["ADMIN"] == 2
        assert ROLE_LEVELS["SUPERVISOR"] == 1

    def test_admin_default_permissions(self):
        assert "PANEL_VIEW" in ADMIN_DEFAULT_PERMISSIONS
        assert "BACKUP_CREATE" not in ADMIN_DEFAULT_PERMISSIONS

    def test_supervisor_default_permissions(self):
        assert "PANEL_VIEW" in SUPERVISOR_DEFAULT_PERMISSIONS
        assert "ADMINS_CREATE" not in SUPERVISOR_DEFAULT_PERMISSIONS

    def test_all_permissions_defined(self):
        assert len(ALL_PERMISSIONS) > 30
        assert "PANEL_VIEW" in ALL_PERMISSIONS
        assert "ADMINS_CREATE" in ALL_PERMISSIONS
