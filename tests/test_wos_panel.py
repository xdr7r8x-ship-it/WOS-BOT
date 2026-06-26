import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


class TestWOSPanel:
    def test_wos_panel_module_import(self):
        try:
            import discord
        except ImportError:
            pytest.skip("discord.py not installed")
        from src.ui.wos_panel import handle_wos_command, handle_button
        assert handle_wos_command is not None
        assert handle_button is not None

    def test_embeds_module_import(self):
        try:
            import discord
        except ImportError:
            pytest.skip("discord.py not installed")
        from src.ui.components.embeds import (
            create_main_embed,
            create_success_embed,
            create_error_embed,
            sanitize_embed_value
        )
        assert create_main_embed is not None
        assert create_success_embed is not None
        assert create_error_embed is not None
        assert sanitize_embed_value is not None

    def test_guards_module_import(self):
        from src.ui.components.guards import (
            check_admin_permission,
            log_panel_action,
            validate_player_id_input
        )
        assert check_admin_permission is not None
        assert log_panel_action is not None
        assert validate_player_id_input is not None

    def test_view_imports(self):
        try:
            import discord
        except ImportError:
            pytest.skip("discord.py not installed")
        from src.ui.views.main_view import MainView
        from src.ui.views.redeem_view import RedeemView
        from src.ui.views.player_view import PlayerView
        from src.ui.views.security_view import SecurityView
        from src.ui.views.system_view import SystemView
        from src.ui.views.backup_view import BackupView
        from src.ui.views.update_view import UpdateView
        from src.ui.views.maintenance_view import MaintenanceView
        assert MainView is not None
        assert RedeemView is not None
        assert PlayerView is not None
        assert SecurityView is not None
        assert SystemView is not None
        assert BackupView is not None
        assert UpdateView is not None
        assert MaintenanceView is not None


class TestWOSPanelEmbeds:
    def test_create_main_embed(self):
        try:
            import discord
        except ImportError:
            pytest.skip("discord.py not installed")
        from src.ui.components.embeds import create_main_embed
        embed = create_main_embed()
        assert embed is not None
        assert embed.title == "WOS Control Panel"

    def test_sanitize_embed_value(self):
        try:
            import discord
        except ImportError:
            pytest.skip("discord.py not installed")
        from src.ui.components.embeds import sanitize_embed_value
        result = sanitize_embed_value("test value", 20)
        assert result == "test value"

    def test_sanitize_embed_value_truncate(self):
        try:
            import discord
        except ImportError:
            pytest.skip("discord.py not installed")
        from src.ui.components.embeds import sanitize_embed_value
        long_text = "a" * 100
        result = sanitize_embed_value(long_text, 20)
        assert len(result) == 20
        assert result.endswith("...")


class TestWOSPanelSecurity:
    def test_unauthorized_embed(self):
        try:
            import discord
        except ImportError:
            pytest.skip("discord.py not installed")
        from src.ui.components.embeds import create_unauthorized_embed
        embed = create_unauthorized_embed()
        assert embed is not None

    def test_custom_id_format(self):
        try:
            import discord
        except ImportError:
            pytest.skip("discord.py not installed")
        from src.ui.views.main_view import MainView
        view = MainView()
        buttons = [item for item in view.children if hasattr(item, 'custom_id')]
        assert len(buttons) > 0
        for btn in buttons:
            assert btn.custom_id.startswith("wos:")
