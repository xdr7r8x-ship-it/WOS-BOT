import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import (
    init_database,
    generate_code_hash,
    register_player,
    get_active_players,
    get_player_count,
    disable_player,
    add_gift_code,
    update_code_status,
    save_processed_code,
    delete_gift_code,
    get_processed_code,
    save_redemption,
    redemption_exists,
    get_redemption_count,
    log_system,
    get_queue_count,
    get_total_success_count,
    get_total_failed_count,
    get_db_size,
    DATABASE_PATH,
)


class TestDatabase:
    @pytest.fixture(autouse=True)
    def setup_database(self):
        if DATABASE_PATH.exists():
            DATABASE_PATH.unlink()
        init_database()
        yield
        if DATABASE_PATH.exists():
            DATABASE_PATH.unlink()

    def test_init_database(self):
        assert DATABASE_PATH.exists()

    def test_register_player(self):
        success, status = register_player("123", "111111")
        assert success is True
        assert status == "SUCCESS"

    def test_get_active_players(self):
        register_player("123", "111111")
        register_player("123", "222222")
        players = get_active_players("123")
        assert len(players) == 2

    def test_get_player_count(self):
        register_player("123", "111111")
        register_player("123", "222222")
        count = get_player_count("123")
        assert count == 2

    def test_disable_player(self):
        register_player("123", "111111")
        result = disable_player("123", "111111")
        assert result is True
        count = get_player_count("123")
        assert count == 0

    def test_add_and_delete_gift_code(self):
        code_hash = generate_code_hash("123", "ABCD1234")
        add_gift_code("123", "ABCD1234", code_hash)
        delete_gift_code("123", code_hash)

    def test_save_processed_code(self):
        code_hash = generate_code_hash("123", "ABCD1234")
        save_processed_code("123", code_hash, "COMPLETED", 5, 3, 2, 1, 0)
        processed = get_processed_code("123", code_hash)
        assert processed is not None
        assert processed["final_status"] == "COMPLETED"
        assert processed["success_count"] == 3

    def test_save_redemption(self):
        code_hash = generate_code_hash("123", "ABCD1234")
        save_redemption("123", code_hash, "111111", "SUCCESS")
        assert redemption_exists("123", code_hash, "111111") is True

    def test_get_redemption_count(self):
        code_hash = generate_code_hash("123", "ABCD1234")
        save_redemption("123", code_hash, "111111", "SUCCESS")
        save_redemption("123", code_hash, "222222", "SUCCESS")
        save_redemption("123", code_hash, "333333", "FAILED")
        counts = get_redemption_count("123", code_hash)
        assert counts["success"] == 2
        assert counts["failed"] == 1

    def test_log_system(self):
        log_system("123", "INFO", "TEST", "Test message")

    def test_get_queue_count(self):
        count = get_queue_count()
        assert count == 0

    def test_get_stats(self):
        code_hash = generate_code_hash("123", "ABCD1234")
        save_processed_code("123", code_hash, "COMPLETED", 5, 3, 2, 1, 0)
        success = get_total_success_count()
        failed = get_total_failed_count()
        assert success == 3
        assert failed == 2

    def test_get_db_size(self):
        size = get_db_size()
        assert "B" in size or "KB" in size or "MB" in size
