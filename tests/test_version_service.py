import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.services.version_service import (
    validate_version, compare_versions,
    get_version_type, is_downgrade
)


class TestVersionService:
    def test_validate_version_valid(self):
        assert validate_version("1.0.0") is True
        assert validate_version("10.20.30") is True
        assert validate_version("0.0.1") is True

    def test_validate_version_invalid(self):
        assert validate_version("1.0") is False
        assert validate_version("1") is False
        assert validate_version("v1.0.0") is False
        assert validate_version("1.0.0.0") is False

    def test_compare_versions_equal(self):
        assert compare_versions("1.0.0", "1.0.0") == 0
        assert compare_versions("10.20.30", "10.20.30") == 0

    def test_compare_versions_greater(self):
        assert compare_versions("1.1.0", "1.0.0") == 1
        assert compare_versions("2.0.0", "1.9.9") == 1
        assert compare_versions("1.0.1", "1.0.0") == 1

    def test_compare_versions_less(self):
        assert compare_versions("1.0.0", "1.1.0") == -1
        assert compare_versions("1.9.9", "2.0.0") == -1
        assert compare_versions("1.0.0", "1.0.1") == -1

    def test_is_downgrade(self):
        assert is_downgrade("2.0.0", "1.0.0") is True
        assert is_downgrade("1.0.0", "2.0.0") is False
        assert is_downgrade("1.0.0", "1.0.0") is False

    def test_get_version_type(self):
        assert get_version_type("1.0.0", "2.0.0") == "MAJOR"
        assert get_version_type("1.0.0", "1.1.0") == "MINOR"
        assert get_version_type("1.0.0", "1.0.1") == "PATCH"
        assert get_version_type("1.0.0", "1.0.0") == "SAME"
