import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.utils.validators import normalize_gift_code, validate_gift_code, extract_codes_from_text


class TestCodeNormalization:
    def test_normalize_uppercase(self):
        assert normalize_gift_code("abc123") == "ABC123"

    def test_normalize_with_spaces(self):
        assert normalize_gift_code("ABC 123") == "ABC123"

    def test_normalize_with_newlines(self):
        assert normalize_gift_code("ABC\n123") == "ABC123"

    def test_normalize_with_tabs(self):
        assert normalize_gift_code("ABC\t123") == "ABC123"

    def test_normalize_empty(self):
        assert normalize_gift_code("") == ""

    def test_normalize_whitespace(self):
        assert normalize_gift_code("  ABC123  ") == "ABC123"


class TestGiftCodeValidation:
    def test_valid_code(self):
        assert validate_gift_code("ABCD1234") is True

    def test_valid_code_min_length(self):
        assert validate_gift_code("ABC1234") is True

    def test_valid_code_max_length(self):
        assert validate_gift_code("ABCD12345678901234") is True

    def test_invalid_code_with_special_chars(self):
        assert validate_gift_code("ABCD-1234") is False

    def test_invalid_code_too_short(self):
        assert validate_gift_code("ABC") is False

    def test_invalid_code_empty(self):
        assert validate_gift_code("") is False

    def test_invalid_code_letters_only(self):
        assert validate_gift_code("ABCDEFGH") is False


class TestCodeExtraction:
    def test_extract_single_code(self):
        codes = extract_codes_from_text("WOSB1234")
        assert codes == ["WOSB1234"]

    def test_extract_multiple_codes(self):
        codes = extract_codes_from_text("WOSB1234 XXXX5678")
        assert set(codes) == {"WOSB1234", "XXXX5678"}

    def test_extract_no_codes(self):
        codes = extract_codes_from_text("No valid codes here!")
        assert codes == []

    def test_extract_from_message(self):
        codes = extract_codes_from_text("Gift code: ABCD1234")
        assert codes == ["ABCD1234"]
