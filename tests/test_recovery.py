import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import (
    init_database,
    generate_code_hash,
    add_gift_code,
    update_code_status,
    get_pending_codes,
    get_stuck_processing_codes,
    DATABASE_PATH,
    now_iso,
)
from datetime import datetime, timedelta


class TestRecovery:
    @pytest.fixture(autouse=True)
    def setup_database(self):
        if DATABASE_PATH.exists():
            DATABASE_PATH.unlink()
        init_database()
        yield
        if DATABASE_PATH.exists():
            DATABASE_PATH.unlink()

    def test_get_pending_codes_empty(self):
        codes = get_pending_codes("123")
        assert len(codes) == 0

    def test_get_pending_codes(self):
        code_hash = generate_code_hash("123", "ABCD1234")
        add_gift_code("123", "ABCD1234", code_hash)
        update_code_status("123", code_hash, "QUEUED")
        codes = get_pending_codes("123")
        assert len(codes) == 1

    def test_get_stuck_processing_codes_empty(self):
        codes = get_stuck_processing_codes("123")
        assert len(codes) == 0

    def test_get_stuck_processing_codes(self):
        code_hash = generate_code_hash("123", "ABCD1234")
        add_gift_code("123", "ABCD1234", code_hash)
        import sqlite3
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        past_time = (datetime.utcnow() - timedelta(minutes=30)).isoformat()
        cursor.execute(
            "UPDATE gift_codes SET status = 'PROCESSING', processing_started_at = ? WHERE code_hash = ?",
            (past_time, code_hash)
        )
        conn.commit()
        conn.close()
        codes = get_stuck_processing_codes("123", minutes=20)
        assert len(codes) == 1
