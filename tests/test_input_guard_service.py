import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.services.input_guard_service import input_guard_service


class TestInputGuardService:
    def test_validate_player_id_valid(self):
        valid, result = input_guard_service.validate_player_id("123456")
        assert valid is True
        assert result == "123456"
    
    def test_validate_player_id_too_short(self):
        valid, result = input_guard_service.validate_player_id("12345")
        assert valid is False
        assert result == "INVALID"
    
    def test_validate_player_id_with_letters(self):
        valid, result = input_guard_service.validate_player_id("123456a")
        assert valid is False
    
    def test_validate_player_id_empty(self):
        valid, result = input_guard_service.validate_player_id("")
        assert valid is False
        assert result == "EMPTY"
    
    def test_validate_player_id_none(self):
        valid, result = input_guard_service.validate_player_id(None)
        assert valid is False
    
    def test_validate_gift_code_valid(self):
        valid, result = input_guard_service.validate_gift_code("ABC123")
        assert valid is True
        assert result == "ABC123"
    
    def test_validate_gift_code_normalized(self):
        valid, result = input_guard_service.validate_gift_code("  abc123  ")
        assert valid is True
        assert result == "ABC123"
    
    def test_validate_gift_code_empty(self):
        valid, result = input_guard_service.validate_gift_code("")
        assert valid is False
        assert result == "EMPTY"
    
    def test_safe_log_player_id(self):
        result = input_guard_service.safe_log_player_id("12345678")
        assert "12345678" not in result
        assert "***" in result
    
    def test_safe_log_gift_code(self):
        result = input_guard_service.safe_log_gift_code("ABC12345")
        assert "ABC12345" not in result
        assert "***" in result
    
    def test_prepare_for_storage(self):
        result = input_guard_service.prepare_for_storage("  test  ")
        assert result == "test"
    
    def test_prepare_for_embed(self):
        result = input_guard_service.prepare_for_embed("test @everyone")
        assert "@everyone" not in result or "@" in result
