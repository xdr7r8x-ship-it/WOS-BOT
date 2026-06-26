import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import (
    init_database,
    generate_code_hash,
    register_player,
    add_gift_code,
    code_exists_in_gift_codes,
    code_exists_in_processed,
    save_redemption,
    redemption_exists,
    get_connection,
    DATABASE_PATH,
)


class TestDuplicatePrevention:
    @pytest.fixture(autouse=True)
    def setup_database(self):
        if DATABASE_PATH.exists():
            DATABASE_PATH.unlink()
        init_database()
        yield
        if DATABASE_PATH.exists():
            DATABASE_PATH.unlink()

    def test_generate_code_hash_consistent(self):
        hash1 = generate_code_hash("123", "ABCD1234")
        hash2 = generate_code_hash("123", "ABCD1234")
        assert hash1 == hash2

    def test_generate_code_hash_different_guilds(self):
        hash1 = generate_code_hash("123", "ABCD1234")
        hash2 = generate_code_hash("456", "ABCD1234")
        assert hash1 != hash2

    def test_generate_code_hash_different_codes(self):
        hash1 = generate_code_hash("123", "ABCD1234")
        hash2 = generate_code_hash("123", "EFGH5678")
        assert hash1 != hash2

    def test_player_registration_unique(self):
        success1, status1 = register_player("123", "111111")
        assert success1 is True
        assert status1 == "SUCCESS"

    def test_player_registration_duplicate(self):
        register_player("123", "111111")
        success2, status2 = register_player("123", "111111")
        assert success2 is False
        assert status2 == "EXISTS"

    def test_different_players_same_guild(self):
        success1, _ = register_player("123", "111111")
        success2, _ = register_player("123", "222222")
        assert success1 is True
        assert success2 is True

    def test_code_not_in_gift_codes(self):
        assert code_exists_in_gift_codes("123", "nonexistent") is False

    def test_add_new_code(self):
        code_hash = generate_code_hash("123", "ABCD1234")
        success, status = add_gift_code("123", "ABCD1234", code_hash)
        assert success is True
        assert status == "CREATED"

    def test_add_duplicate_code(self):
        code_hash = generate_code_hash("123", "ABCD1234")
        add_gift_code("123", "ABCD1234", code_hash)
        success2, status2 = add_gift_code("123", "ABCD1234", code_hash)
        assert success2 is False
        assert status2 == "EXISTS"

    def test_redemption_saved(self):
        code_hash = generate_code_hash("123", "ABCD1234")
        save_redemption("123", code_hash, "111111", "SUCCESS")
        assert redemption_exists("123", code_hash, "111111") is True

    def test_same_player_same_code_prevented(self):
        code_hash = generate_code_hash("123", "ABCD1234")
        save_redemption("123", code_hash, "111111", "SUCCESS")
        assert redemption_exists("123", code_hash, "111111") is True
