import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.utils.validators import validate_player_id


class TestPlayerIdValidation:
    def test_valid_player_id_6_digits(self):
        assert validate_player_id("123456") is True

    def test_valid_player_id_7_digits(self):
        assert validate_player_id("1234567") is True

    def test_valid_player_id_15_digits(self):
        assert validate_player_id("123456789012345") is True

    def test_valid_player_id_max(self):
        assert validate_player_id("999999999999999") is True

    def test_invalid_player_id_with_name(self):
        assert validate_player_id("12345678 Mansour") is False

    def test_invalid_player_id_with_space(self):
        assert validate_player_id("123456 789") is False

    def test_invalid_player_id_with_letters(self):
        assert validate_player_id("abc123") is False

    def test_invalid_player_id_too_short(self):
        assert validate_player_id("123") is False

    def test_invalid_player_id_too_long(self):
        assert validate_player_id("1234567890123456") is False

    def test_invalid_player_id_empty(self):
        assert validate_player_id("") is False

    def test_invalid_player_id_none(self):
        assert validate_player_id(None) is False

    def test_invalid_player_id_with_symbols(self):
        assert validate_player_id("123456!") is False

    def test_invalid_player_id_newline(self):
        assert validate_player_id("123456\n789") is False
