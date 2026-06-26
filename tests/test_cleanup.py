import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import (
    init_database,
    generate_code_hash,
    register_player,
    add_gift_code,
    update_code_status,
    save_redemption,
    save_processed_code,
    add_retry_job,
    cleanup_old_data,
    DATABASE_PATH,
)
from datetime import datetime, timedelta


class TestCleanup:
    @pytest.fixture(autouse=True)
    def setup_database(self):
        if DATABASE_PATH.exists():
            DATABASE_PATH.unlink()
        init_database()
        yield
        if DATABASE_PATH.exists():
            DATABASE_PATH.unlink()

    def test_cleanup_no_errors(self):
        cleanup_old_data()

    def test_cleanup_with_old_data(self):
        code_hash = generate_code_hash("123", "ABCD1234")
        save_redemption("123", code_hash, "111111", "SUCCESS")
        cleanup_old_data()
