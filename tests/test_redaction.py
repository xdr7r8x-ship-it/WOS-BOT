import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.utils.redaction import mask_secret, redact_text, redact_dict, safe_log_value


class TestRedaction:
    def test_mask_secret_long_value(self):
        result = mask_secret("abcdefghijklmnop")
        assert result.startswith("abcd")
        assert result.endswith("mnop")
        assert "***" in result
        assert "abcdefghijklmnop" not in result
    
    def test_mask_secret_short_value(self):
        result = mask_secret("short")
        assert result == "***REDACTED***"
    
    def test_mask_secret_non_string(self):
        result = mask_secret(12345)
        assert result == "***REDACTED***"
    
    def test_redact_text_with_token(self):
        text = "GitHub token: ghp_abcdefghij1234567890klmnopqrstuvwx"
        result = redact_text(text)
        assert "ghp_" not in result
    
    def test_redact_text_with_github_token(self):
        text = "GitHub token: ghp_abcdefghij1234567890klmnopqrstuvwx"
        result = redact_text(text)
        assert "ghp_" not in result
    
    def test_redact_dict(self):
        data = {
            "username": "test",
            "password": "secret123",
            "api_key": "key1234567890abcdef"
        }
        result = redact_dict(data)
        assert result.get("username") == "test"
        assert "secret" not in str(result.get("password", ""))
        assert "key1234" not in str(result.get("api_key", ""))
    
    def test_redact_dict_nested(self):
        data = {
            "user": {
                "name": "test",
                "credentials": {
                    "token": "secret_token"
                }
            }
        }
        result = redact_dict(data)
        assert result.get("user", {}).get("name") == "test"
        assert "secret" not in str(result.get("user", {}).get("credentials", {}).get("token", ""))
    
    def test_safe_log_value_string(self):
        result = safe_log_value("test_string")
        assert isinstance(result, str)
    
    def test_safe_log_value_none(self):
        result = safe_log_value(None)
        assert result == "None"
    
    def test_safe_log_value_int(self):
        result = safe_log_value(12345)
        assert result == "12345"
    
    def test_safe_log_value_with_secret(self):
        text = "GitHub token: ghp_abcdefghij1234567890klmnopqrstuvwx"
        result = safe_log_value(text)
        assert "ghp_" not in result
