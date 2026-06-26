import pytest
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture(scope="function", autouse=True)
def init_all_tables():
    from database import (
        init_database,
        init_autopilot_tables,
        init_alliance_tables,
        init_language_table,
        init_content_tables,
        init_reminder_tables,
        init_player_id_service_tables,
        init_feature_registry_tables,
        init_security_tables,
    )
    
    init_database()
    init_autopilot_tables()
    init_alliance_tables()
    init_language_table()
    init_content_tables()
    init_reminder_tables()
    init_player_id_service_tables()
    init_feature_registry_tables()
    init_security_tables()
    
    yield
