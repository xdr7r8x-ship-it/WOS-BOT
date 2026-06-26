import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


class TestDiscordGuardService:
    def test_discord_guard_import(self):
        from src.services.discord_guard_service import discord_guard_service
        assert discord_guard_service is not None
    
    def test_discord_guard_has_methods(self):
        from src.services.discord_guard_service import discord_guard_service
        assert hasattr(discord_guard_service, 'get_allowed_mentions')
        assert hasattr(discord_guard_service, 'clean_content')
        assert hasattr(discord_guard_service, 'sanitize_for_embed')
    
    def test_get_allowed_mentions(self):
        try:
            import discord
        except ImportError:
            return
        from src.services.discord_guard_service import discord_guard_service
        mentions = discord_guard_service.get_allowed_mentions()
        assert mentions is not None
    
    def test_clean_content(self):
        from src.services.discord_guard_service import discord_guard_service
        result = discord_guard_service.clean_content("Hello @everyone")
        assert "@everyone" not in result
    
    def test_clean_content_with_mention(self):
        from src.services.discord_guard_service import discord_guard_service
        result = discord_guard_service.clean_content("Hello <@123456>")
        assert "@everyone" not in result
    
    def test_sanitize_for_embed(self):
        from src.services.discord_guard_service import discord_guard_service
        result = discord_guard_service.sanitize_for_embed("Test {variable}")
        assert "\u200b{" in result
    
    def test_extract_safe_content(self):
        from src.services.discord_guard_service import discord_guard_service
        result = discord_guard_service.extract_safe_content("Hello @everyone")
        assert "@everyone" not in result
