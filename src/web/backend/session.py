import sqlite3
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from .security import generate_session_id
from .config import config


class SessionManager:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def create_session(
        self,
        user_id: str,
        guild_id: Optional[str],
        role_level: str
    ) -> str:
        session_id = generate_session_id()
        session_hash = session_id[:16]
        expires_at = (datetime.utcnow() + timedelta(hours=config.WEB_SESSION_TTL_HOURS)).isoformat()
        now = datetime.utcnow().isoformat()

        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO web_sessions (session_id_hash, guild_id, user_id, role_level, expires_at, created_at, last_seen_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (session_hash, guild_id, user_id, role_level, expires_at, now, now)
            )
            conn.commit()

        return session_id

    def validate_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        session_hash = session_id[:16]
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                """
                SELECT * FROM web_sessions 
                WHERE session_id_hash = ? AND revoked = 0 AND expires_at > ?
                """,
                (session_hash, datetime.utcnow().isoformat())
            ).fetchone()

            if row:
                conn.execute(
                    "UPDATE web_sessions SET last_seen_at = ? WHERE session_id_hash = ?",
                    (datetime.utcnow().isoformat(), session_hash)
                )
                conn.commit()
                return dict(row)
        return None

    def revoke_session(self, session_id: str) -> bool:
        session_hash = session_id[:16]
        with self._get_connection() as conn:
            conn.execute(
                "UPDATE web_sessions SET revoked = 1 WHERE session_id_hash = ?",
                (session_hash,)
            )
            conn.commit()
            return conn.total_changes > 0

    def revoke_all_user_sessions(self, user_id: str) -> int:
        with self._get_connection() as conn:
            conn.execute(
                "UPDATE web_sessions SET revoked = 1 WHERE user_id = ?",
                (user_id,)
            )
            conn.commit()
            return conn.total_changes


def get_session_manager() -> SessionManager:
    return SessionManager(config.DATABASE_PATH)
