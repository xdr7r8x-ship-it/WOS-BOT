import pytest
import os


class TestGiftCodeRoutes:
    def test_gift_code_routes_module_exists(self):
        assert os.path.exists("src/web/backend/routes/gift_code_routes.py")

    def test_gift_code_redeem_endpoint_defined(self):
        with open("src/web/backend/routes/gift_code_routes.py") as f:
            content = f.read()
            assert '"/redeem"' in content or '@router.post' in content

    def test_gift_code_list_endpoint_defined(self):
        with open("src/web/backend/routes/gift_code_routes.py") as f:
            content = f.read()
            assert 'router.get' in content or '@router.get' in content


class TestPlayerRoutes:
    def test_player_routes_module_exists(self):
        assert os.path.exists("src/web/backend/routes/player_routes.py")

    def test_player_list_endpoint_defined(self):
        with open("src/web/backend/routes/player_routes.py") as f:
            content = f.read()
            assert 'router.get' in content or '@router.get' in content


class TestAllianceRoutes:
    def test_alliance_routes_module_exists(self):
        assert os.path.exists("src/web/backend/routes/alliance_routes.py")

    def test_alliance_list_endpoint_defined(self):
        with open("src/web/backend/routes/alliance_routes.py") as f:
            content = f.read()
            assert 'router.get' in content or '@router.get' in content


class TestReminderRoutes:
    def test_reminder_routes_module_exists(self):
        assert os.path.exists("src/web/backend/routes/reminder_routes.py")

    def test_reminder_list_endpoint_defined(self):
        with open("src/web/backend/routes/reminder_routes.py") as f:
            content = f.read()
            assert 'router.get' in content or '@router.get' in content


class TestDashboardRoutes:
    def test_dashboard_routes_module_exists(self):
        assert os.path.exists("src/web/backend/routes/dashboard_routes.py")

    def test_dashboard_health_endpoint_defined(self):
        with open("src/web/backend/routes/dashboard_routes.py") as f:
            content = f.read()
            assert 'health' in content.lower()


class TestAuthRoutes:
    def test_auth_routes_module_exists(self):
        assert os.path.exists("src/web/backend/routes/auth_routes.py")

    def test_auth_login_endpoint_defined(self):
        with open("src/web/backend/routes/auth_routes.py") as f:
            content = f.read()
            assert 'login' in content.lower()


class TestSystemRoutes:
    def test_system_routes_module_exists(self):
        assert os.path.exists("src/web/backend/routes/system_routes.py")


class TestBackupRoutes:
    def test_backup_routes_module_exists(self):
        assert os.path.exists("src/web/backend/routes/backup_routes.py")


class TestUpdateRoutes:
    def test_update_routes_module_exists(self):
        assert os.path.exists("src/web/backend/routes/update_routes.py")


class TestSecurityRoutes:
    def test_security_routes_module_exists(self):
        assert os.path.exists("src/web/backend/routes/security_routes.py")


class TestAuditRoutes:
    def test_audit_routes_module_exists(self):
        assert os.path.exists("src/web/backend/routes/audit_routes.py")


class TestContentRoutes:
    def test_content_routes_module_exists(self):
        assert os.path.exists("src/web/backend/routes/content_routes.py")


class TestAllianceApiRoutes:
    def test_alliance_api_routes_module_exists(self):
        assert os.path.exists("src/web/backend/routes/alliance_api_routes.py")


class TestPlayerPanelRoutes:
    def test_player_panel_routes_module_exists(self):
        assert os.path.exists("src/web/backend/routes/player_panel_routes.py")


class TestAdminRoutes:
    def test_admin_routes_module_exists(self):
        assert os.path.exists("src/web/backend/routes/admin_routes.py")
