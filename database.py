import asyncio
import hashlib
import logging
import os
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

DATABASE_DIR = Path("db")
DATABASE_DIR.mkdir(exist_ok=True)

DATABASE_PATH = DATABASE_DIR / "wos_bot.db"

LOCK = threading.RLock()

PRAGMAS = """
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;
PRAGMA foreign_keys=ON;
PRAGMA busy_timeout=5000;
"""

logger = logging.getLogger(__name__)


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DATABASE_PATH, timeout=30.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=5000")
    return conn


@contextmanager
def get_db():
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()


def with_retry(func):
    def wrapper(*args, **kwargs):
        for attempt in range(3):
            try:
                with LOCK:
                    return func(*args, **kwargs)
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e) and attempt < 2:
                    logger.warning(f"Database locked, retrying ({attempt + 1}/3)")
                    continue
                raise
    return wrapper


def init_database():
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS guild_settings (
                guild_id TEXT PRIMARY KEY,
                register_channel_id TEXT,
                codes_channel_id TEXT,
                log_channel_id TEXT,
                admin_role_id TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id TEXT NOT NULL,
                player_id TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'ACTIVE',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(guild_id, player_id)
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_players_guild_status ON players(guild_id, status)
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                role_level TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'ACTIVE',
                created_by TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(guild_id, user_id)
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_admin_users_guild_status ON admin_users(guild_id, status)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_admin_users_user ON admin_users(user_id)
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_permissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                permission_key TEXT NOT NULL,
                enabled INTEGER NOT NULL DEFAULT 1,
                granted_by TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(guild_id, user_id, permission_key)
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_admin_permissions_lookup ON admin_permissions(guild_id, user_id, permission_key)
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_permission_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id TEXT NOT NULL,
                template_name TEXT NOT NULL,
                permissions_json TEXT NOT NULL,
                created_by TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(guild_id, template_name)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS access_denials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id TEXT,
                user_id TEXT NOT NULL,
                action TEXT NOT NULL,
                reason TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_access_denials_user_created ON access_denials(user_id, created_at)
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gift_codes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id TEXT NOT NULL,
                code TEXT NOT NULL,
                code_hash TEXT NOT NULL,
                status TEXT NOT NULL,
                source_message_id TEXT,
                created_at TEXT NOT NULL,
                processing_started_at TEXT,
                completed_at TEXT,
                UNIQUE(guild_id, code_hash)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS processed_codes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id TEXT NOT NULL,
                code_hash TEXT NOT NULL,
                final_status TEXT NOT NULL,
                total_players INTEGER NOT NULL DEFAULT 0,
                success_count INTEGER NOT NULL DEFAULT 0,
                failed_count INTEGER NOT NULL DEFAULT 0,
                retry_count INTEGER NOT NULL DEFAULT 0,
                verification_count INTEGER NOT NULL DEFAULT 0,
                processed_at TEXT NOT NULL,
                UNIQUE(guild_id, code_hash)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS redemption_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id TEXT NOT NULL,
                code_hash TEXT NOT NULL,
                player_id TEXT NOT NULL,
                status TEXT NOT NULL,
                error_type TEXT,
                attempt_count INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                UNIQUE(guild_id, code_hash, player_id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS retry_jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id TEXT NOT NULL,
                code_hash TEXT NOT NULL,
                player_id TEXT NOT NULL,
                reason TEXT NOT NULL,
                attempts INTEGER NOT NULL DEFAULT 0,
                next_retry_at TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'PENDING',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(guild_id, code_hash, player_id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id TEXT,
                level TEXT NOT NULL,
                event TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_players_guild_status ON players(guild_id, status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_players_player_id ON players(player_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_gift_codes_guild_status ON gift_codes(guild_id, status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_gift_codes_hash ON gift_codes(code_hash)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_processed_codes_hash ON processed_codes(code_hash)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_redemption_history_code_player ON redemption_history(guild_id, code_hash, player_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_retry_jobs_due ON retry_jobs(status, next_retry_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_guild_created ON system_logs(guild_id, created_at)")
        
        conn.commit()


def now_iso():
    return datetime.utcnow().isoformat()


def generate_code_hash(guild_id: str, code: str) -> str:
    normalized = code.strip().upper().replace(" ", "").replace("\n", "").replace("\r", "")
    return hashlib.sha256(f"{guild_id}:{normalized}".encode()).hexdigest()


def get_guild_settings(guild_id: str) -> Optional[dict]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM guild_settings WHERE guild_id = ?", (guild_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def save_guild_settings(guild_id: str, **kwargs):
    with get_db() as conn:
        cursor = conn.cursor()
        existing = get_guild_settings(guild_id)
        if existing:
            updates = []
            values = []
            for key, value in kwargs.items():
                if value is not None:
                    updates.append(f"{key} = ?")
                    values.append(value)
            if updates:
                updates.append("updated_at = ?")
                values.append(now_iso())
                values.append(guild_id)
                cursor.execute(
                    f"UPDATE guild_settings SET {', '.join(updates)} WHERE guild_id = ?",
                    values
                )
        else:
            cursor.execute(
                """INSERT INTO guild_settings 
                   (guild_id, register_channel_id, codes_channel_id, log_channel_id, admin_role_id, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (guild_id, kwargs.get('register_channel_id'), kwargs.get('codes_channel_id'),
                 kwargs.get('log_channel_id'), kwargs.get('admin_role_id'), now_iso(), now_iso())
            )
        conn.commit()


def register_player(guild_id: str, player_id: str) -> tuple[bool, str]:
    with get_db() as conn:
        cursor = conn.cursor()
        existing = cursor.execute(
            "SELECT id FROM players WHERE guild_id = ? AND player_id = ?",
            (guild_id, player_id)
        ).fetchone()
        
        if existing:
            return False, "EXISTS"
        
        try:
            cursor.execute(
                """INSERT INTO players (guild_id, player_id, status, created_at, updated_at)
                   VALUES (?, ?, 'ACTIVE', ?, ?)""",
                (guild_id, player_id, now_iso(), now_iso())
            )
            conn.commit()
            return True, "SUCCESS"
        except sqlite3.IntegrityError:
            return False, "EXISTS"


def get_active_players(guild_id: str) -> list:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT player_id FROM players WHERE guild_id = ? AND status = 'ACTIVE'",
            (guild_id,)
        )
        return [row[0] for row in cursor.fetchall()]


def disable_player(guild_id: str, player_id: str) -> bool:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE players SET status = 'DISABLED', updated_at = ? WHERE guild_id = ? AND player_id = ?",
            (now_iso(), guild_id, player_id)
        )
        conn.commit()
        return cursor.rowcount > 0


def get_player_count(guild_id: str) -> int:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM players WHERE guild_id = ? AND status = 'ACTIVE'",
            (guild_id,)
        )
        return cursor.fetchone()[0]


def code_exists_in_gift_codes(guild_id: str, code_hash: str) -> bool:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT 1 FROM gift_codes WHERE guild_id = ? AND code_hash = ?",
            (guild_id, code_hash)
        )
        return cursor.fetchone() is not None


def code_exists_in_processed(guild_id: str, code_hash: str) -> bool:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT 1 FROM processed_codes WHERE guild_id = ? AND code_hash = ?",
            (guild_id, code_hash)
        )
        return cursor.fetchone() is not None


def add_gift_code(guild_id: str, code: str, code_hash: str, message_id: str = None) -> tuple[bool, str]:
    if code_exists_in_gift_codes(guild_id, code_hash) or code_exists_in_processed(guild_id, code_hash):
        return False, "EXISTS"
    
    with get_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                """INSERT INTO gift_codes (guild_id, code, code_hash, status, source_message_id, created_at)
                   VALUES (?, ?, ?, 'NEW', ?, ?)""",
                (guild_id, code, code_hash, message_id, now_iso())
            )
            conn.commit()
            return True, "CREATED"
        except sqlite3.IntegrityError:
            return False, "EXISTS"


def get_code_by_hash(guild_id: str, code_hash: str) -> Optional[dict]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM gift_codes WHERE guild_id = ? AND code_hash = ?",
            (guild_id, code_hash)
        )
        row = cursor.fetchone()
        return dict(row) if row else None


def update_code_status(guild_id: str, code_hash: str, status: str):
    with get_db() as conn:
        cursor = conn.cursor()
        if status == 'PROCESSING':
            cursor.execute(
                "UPDATE gift_codes SET status = ?, processing_started_at = ? WHERE guild_id = ? AND code_hash = ?",
                (status, now_iso(), guild_id, code_hash)
            )
        elif status in ('COMPLETED', 'FAILED', 'EXPIRED', 'API_PAUSED', 'NEEDS_VERIFICATION'):
            cursor.execute(
                "UPDATE gift_codes SET status = ?, completed_at = ? WHERE guild_id = ? AND code_hash = ?",
                (status, now_iso(), guild_id, code_hash)
            )
        else:
            cursor.execute(
                "UPDATE gift_codes SET status = ? WHERE guild_id = ? AND code_hash = ?",
                (status, guild_id, code_hash)
            )
        conn.commit()


def get_pending_codes(guild_id: str) -> list:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT code_hash, code FROM gift_codes WHERE guild_id = ? AND status IN ('NEW', 'QUEUED')",
            (guild_id,)
        )
        return [{"code_hash": row[0], "code": row[1]} for row in cursor.fetchall()]


def get_stuck_processing_codes(guild_id: str, minutes: int = 20) -> list:
    cutoff = (datetime.utcnow() - timedelta(minutes=minutes)).isoformat()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT code_hash, code FROM gift_codes 
               WHERE guild_id = ? AND status = 'PROCESSING' AND processing_started_at < ?""",
            (guild_id, cutoff)
        )
        return [{"code_hash": row[0], "code": row[1]} for row in cursor.fetchall()]


def save_redemption(guild_id: str, code_hash: str, player_id: str, status: str, 
                    error_type: str = None, attempt_count: int = 0) -> bool:
    with get_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                """INSERT INTO redemption_history 
                   (guild_id, code_hash, player_id, status, error_type, attempt_count, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (guild_id, code_hash, player_id, status, error_type, attempt_count, now_iso())
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            cursor.execute(
                """UPDATE redemption_history 
                   SET status = ?, error_type = ?, attempt_count = ?
                   WHERE guild_id = ? AND code_hash = ? AND player_id = ?""",
                (status, error_type, attempt_count, guild_id, code_hash, player_id)
            )
            conn.commit()
            return True


def redemption_exists(guild_id: str, code_hash: str, player_id: str) -> bool:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT 1 FROM redemption_history WHERE guild_id = ? AND code_hash = ? AND player_id = ?",
            (guild_id, code_hash, player_id)
        )
        return cursor.fetchone() is not None


def get_redemption_count(guild_id: str, code_hash: str) -> dict:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT status, COUNT(*) FROM redemption_history 
               WHERE guild_id = ? AND code_hash = ?
               GROUP BY status""",
            (guild_id, code_hash)
        )
        results = cursor.fetchall()
        counts = {"success": 0, "failed": 0, "needs_verification": 0}
        for status, count in results:
            if status == "SUCCESS":
                counts["success"] = count
            elif status == "NEEDS_VERIFICATION":
                counts["needs_verification"] = count
            else:
                counts["failed"] += count
        return counts


def save_processed_code(guild_id: str, code_hash: str, final_status: str, total_players: int,
                        success_count: int, failed_count: int, retry_count: int = 0,
                        verification_count: int = 0):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT OR REPLACE INTO processed_codes 
               (guild_id, code_hash, final_status, total_players, success_count, failed_count,
                retry_count, verification_count, processed_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (guild_id, code_hash, final_status, total_players, success_count, failed_count,
             retry_count, verification_count, now_iso())
        )
        conn.commit()


def get_processed_code(guild_id: str, code_hash: str) -> Optional[dict]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM processed_codes WHERE guild_id = ? AND code_hash = ?",
            (guild_id, code_hash)
        )
        row = cursor.fetchone()
        return dict(row) if row else None


def delete_gift_code(guild_id: str, code_hash: str) -> bool:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM gift_codes WHERE guild_id = ? AND code_hash = ?",
            (guild_id, code_hash)
        )
        conn.commit()
        return cursor.rowcount > 0


def add_retry_job(guild_id: str, code_hash: str, player_id: str, reason: str, 
                  next_retry_at: str = None) -> bool:
    if next_retry_at is None:
        next_retry_at = (datetime.utcnow() + timedelta(seconds=30)).isoformat()
    
    with get_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                """INSERT INTO retry_jobs 
                   (guild_id, code_hash, player_id, reason, attempts, next_retry_at, status, created_at, updated_at)
                   VALUES (?, ?, ?, ?, 0, ?, 'PENDING', ?, ?)""",
                (guild_id, code_hash, player_id, reason, next_retry_at, now_iso(), now_iso())
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False


def get_due_retry_jobs(limit: int = 100) -> list:
    current = datetime.utcnow().isoformat()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT * FROM retry_jobs 
               WHERE status = 'PENDING' AND next_retry_at <= ?
               ORDER BY next_retry_at ASC LIMIT ?""",
            (current, limit)
        )
        return [dict(row) for row in cursor.fetchall()]


def update_retry_job(job_id: int, status: str, next_retry_at: str = None, increment_attempts: bool = True):
    with get_db() as conn:
        cursor = conn.cursor()
        if increment_attempts:
            if next_retry_at:
                cursor.execute(
                    """UPDATE retry_jobs SET status = ?, next_retry_at = ?, 
                       attempts = attempts + 1, updated_at = ? WHERE id = ?""",
                    (status, next_retry_at, now_iso(), job_id)
                )
            else:
                cursor.execute(
                    """UPDATE retry_jobs SET status = ?, attempts = attempts + 1, updated_at = ? 
                       WHERE id = ?""",
                    (status, now_iso(), job_id)
                )
        else:
            cursor.execute(
                """UPDATE retry_jobs SET status = ?, updated_at = ? WHERE id = ?""",
                (status, now_iso(), job_id)
            )
        conn.commit()


def get_retry_job_count() -> int:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM retry_jobs WHERE status = 'PENDING'")
        return cursor.fetchone()[0]


def get_pending_redemptions(guild_id: str, code_hash: str) -> list:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT player_id FROM redemption_history 
               WHERE guild_id = ? AND code_hash = ? AND status NOT IN ('SUCCESS', 'SKIPPED_DUPLICATE', 'NEEDS_VERIFICATION')""",
            (guild_id, code_hash)
        )
        return [row[0] for row in cursor.fetchall()]


def log_system(guild_id: str, level: str, event: str, message: str):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO system_logs (guild_id, level, event, message, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            (guild_id, level, event, message, now_iso())
        )
        conn.commit()


def cleanup_old_data():
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute(
            """DELETE FROM redemption_history 
               WHERE created_at < ?""",
            ((datetime.utcnow() - timedelta(days=30)).isoformat(),)
        )
        
        cursor.execute(
            """DELETE FROM retry_jobs 
               WHERE status IN ('DONE', 'FAILED') AND updated_at < ?""",
            ((datetime.utcnow() - timedelta(days=7)).isoformat(),)
        )
        
        for guild_id in get_all_guild_ids():
            cursor.execute(
                """DELETE FROM system_logs WHERE guild_id = ? AND id NOT IN 
                   (SELECT id FROM system_logs WHERE guild_id = ? ORDER BY created_at DESC LIMIT 5000)""",
                (guild_id, guild_id)
            )
        
        conn.commit()


def get_all_guild_ids() -> list:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT guild_id FROM guild_settings")
        return [row[0] for row in cursor.fetchall()]


def get_queue_count() -> int:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM gift_codes WHERE status IN ('NEW', 'QUEUED', 'PROCESSING')")
        return cursor.fetchone()[0]


def get_total_success_count() -> int:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(success_count) FROM processed_codes")
        result = cursor.fetchone()[0]
        return result if result else 0


def get_total_failed_count() -> int:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(failed_count) FROM processed_codes")
        result = cursor.fetchone()[0]
        return result if result else 0


def get_db_size() -> str:
    if DATABASE_PATH.exists():
        size = DATABASE_PATH.stat().st_size
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / (1024 * 1024):.1f} MB"
    return "0 KB"


def get_gift_codes_to_delete(guild_id: str) -> list:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT code_hash FROM gift_codes 
               WHERE guild_id = ? AND status IN ('COMPLETED', 'FAILED', 'EXPIRED')""",
            (guild_id,)
        )
        return [row[0] for row in cursor.fetchall()]


def init_autopilot_tables():
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_state (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS service_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_name TEXT UNIQUE NOT NULL,
                status TEXT NOT NULL DEFAULT 'STOPPED',
                last_heartbeat TEXT,
                restart_count INTEGER DEFAULT 0,
                consecutive_failures INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                migration_id TEXT UNIQUE NOT NULL,
                applied_at TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'APPLIED',
                rollback_sql TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS backups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                backup_name TEXT NOT NULL,
                backup_path TEXT NOT NULL,
                size_bytes INTEGER,
                status TEXT NOT NULL DEFAULT 'COMPLETED',
                created_at TEXT NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS update_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_version TEXT NOT NULL,
                to_version TEXT NOT NULL,
                status TEXT NOT NULL,
                applied_at TEXT,
                rolled_back_at TEXT,
                notes TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS health_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                message TEXT NOT NULL,
                details TEXT,
                created_at TEXT NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS service_locks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lock_name TEXT UNIQUE NOT NULL,
                acquired_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                holder TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prediction_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prediction_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                message TEXT NOT NULL,
                details TEXT,
                created_at TEXT NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS security_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                message TEXT NOT NULL,
                details TEXT,
                created_at TEXT NOT NULL
            )
        """)
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_service_name ON service_status(service_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_locks_expires ON service_locks(expires_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_health_created ON health_events(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_predictions_created ON prediction_events(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_security_created ON security_events(created_at)")
        
        conn.commit()


def save_system_state(key: str, value: str):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT OR REPLACE INTO system_state (key, value, updated_at) VALUES (?, ?, ?)""",
            (key, value, now_iso())
        )
        conn.commit()


def get_system_state(key: str) -> Optional[str]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM system_state WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row[0] if row else None


def save_service_status(service_name: str, status: str, heartbeat: bool = False):
    with get_db() as conn:
        cursor = conn.cursor()
        if heartbeat:
            cursor.execute(
                """UPDATE service_status SET status = ?, last_heartbeat = ?, updated_at = ?
                   WHERE service_name = ?""",
                (status, now_iso(), now_iso(), service_name)
            )
        else:
            cursor.execute(
                """INSERT OR REPLACE INTO service_status 
                   (service_name, status, last_heartbeat, restart_count, consecutive_failures, created_at, updated_at)
                   VALUES (?, ?, ?, 0, 0, ?, ?)""",
                (service_name, status, now_iso(), now_iso(), now_iso())
            )
        conn.commit()


def get_service_status(service_name: str) -> Optional[dict]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM service_status WHERE service_name = ?", (service_name,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_all_service_status() -> list:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM service_status ORDER BY service_name")
        return [dict(row) for row in cursor.fetchall()]


def record_service_failure(service_name: str):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE service_status SET consecutive_failures = consecutive_failures + 1, 
               restart_count = restart_count + 1, updated_at = ? WHERE service_name = ?""",
            (now_iso(), service_name)
        )
        conn.commit()


def reset_service_failures(service_name: str):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE service_status SET consecutive_failures = 0, updated_at = ? WHERE service_name = ?""",
            (now_iso(), service_name)
        )
        conn.commit()


def save_health_event(event_type: str, severity: str, message: str, details: str = None):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO health_events (event_type, severity, message, details, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            (event_type, severity, message, details, now_iso())
        )
        conn.commit()


def get_health_events(limit: int = 100) -> list:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM health_events ORDER BY created_at DESC LIMIT ?",
            (limit,)
        )
        return [dict(row) for row in cursor.fetchall()]


def acquire_lock(lock_name: str, ttl_seconds: int = 60) -> bool:
    with get_db() as conn:
        cursor = conn.cursor()
        expires_at = (datetime.utcnow() + timedelta(seconds=ttl_seconds)).isoformat()
        try:
            cursor.execute(
                """INSERT INTO service_locks (lock_name, acquired_at, expires_at)
                   VALUES (?, ?, ?)""",
                (lock_name, now_iso(), expires_at)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            cursor.execute(
                "DELETE FROM service_locks WHERE lock_name = ? AND expires_at < ?",
                (lock_name, now_iso())
            )
            conn.commit()
            try:
                cursor.execute(
                    """INSERT INTO service_locks (lock_name, acquired_at, expires_at)
                       VALUES (?, ?, ?)""",
                    (lock_name, now_iso(), expires_at)
                )
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False


def release_lock(lock_name: str):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM service_locks WHERE lock_name = ?", (lock_name,))
        conn.commit()


def cleanup_expired_locks():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM service_locks WHERE expires_at < ?", (now_iso(),))
        conn.commit()
        return cursor.rowcount


def save_backup(backup_name: str, backup_path: str, size_bytes: int, status: str = "COMPLETED") -> int:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO backups (backup_name, backup_path, size_bytes, status, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            (backup_name, backup_path, size_bytes, status, now_iso())
        )
        conn.commit()
        return cursor.lastrowid


def get_backups(limit: int = 10) -> list:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM backups ORDER BY created_at DESC LIMIT ?",
            (limit,)
        )
        return [dict(row) for row in cursor.fetchall()]


def get_latest_backup() -> Optional[dict]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM backups WHERE status = 'COMPLETED' ORDER BY created_at DESC LIMIT 1"
        )
        row = cursor.fetchone()
        return dict(row) if row else None


def save_prediction_event(prediction_type: str, severity: str, message: str, details: str = None):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO prediction_events (prediction_type, severity, message, details, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            (prediction_type, severity, message, details, now_iso())
        )
        conn.commit()


def get_prediction_events(limit: int = 100) -> list:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM prediction_events ORDER BY created_at DESC LIMIT ?",
            (limit,)
        )
        return [dict(row) for row in cursor.fetchall()]


def save_security_event(event_type: str, severity: str, message: str, details: str = None):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO security_events (event_type, severity, message, details, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            (event_type, severity, message, details, now_iso())
        )
        conn.commit()


def get_security_events(limit: int = 100) -> list:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM security_events ORDER BY created_at DESC LIMIT ?",
            (limit,)
        )
        return [dict(row) for row in cursor.fetchall()]


def save_migration(migration_id: str, rollback_sql: str = None):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO migrations (migration_id, applied_at, status, rollback_sql)
               VALUES (?, ?, 'APPLIED', ?)""",
            (migration_id, now_iso(), rollback_sql)
        )
        conn.commit()


def get_migrations() -> list:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM migrations ORDER BY applied_at DESC")
        return [dict(row) for row in cursor.fetchall()]


def migration_exists(migration_id: str) -> bool:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM migrations WHERE migration_id = ?", (migration_id,))
        return cursor.fetchone() is not None


def save_update_history(from_version: str, to_version: str, status: str, notes: str = None):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO update_history (from_version, to_version, status, applied_at, notes)
               VALUES (?, ?, ?, ?, ?)""",
            (from_version, to_version, status, now_iso(), notes)
        )
        conn.commit()


def get_update_history(limit: int = 10) -> list:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM update_history ORDER BY applied_at DESC LIMIT ?",
            (limit,)
        )
        return [dict(row) for row in cursor.fetchall()]


def cleanup_old_health_events(days: int = 30):
    with get_db() as conn:
        cursor = conn.cursor()
        cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
        cursor.execute("DELETE FROM health_events WHERE created_at < ?", (cutoff,))
        conn.commit()


def cleanup_old_predictions(days: int = 7):
    with get_db() as conn:
        cursor = conn.cursor()
        cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
        cursor.execute("DELETE FROM prediction_events WHERE created_at < ?", (cutoff,))
        conn.commit()


def init_alliance_tables():
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alliances (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id TEXT NOT NULL,
                alliance_external_id TEXT,
                alliance_tag TEXT NOT NULL,
                alliance_name TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'ACTIVE',
                source TEXT NOT NULL DEFAULT 'MANUAL',
                last_synced_at TEXT,
                created_by TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(guild_id, alliance_tag)
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_alliances_guild_status ON alliances(guild_id, status)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_alliances_external ON alliances(guild_id, alliance_external_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_alliances_tag ON alliances(guild_id, alliance_tag)
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alliance_members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id TEXT NOT NULL,
                alliance_id INTEGER NOT NULL,
                player_id TEXT NOT NULL,
                external_member_id TEXT,
                alliance_rank TEXT NOT NULL DEFAULT 'R1',
                status TEXT NOT NULL DEFAULT 'ACTIVE',
                source TEXT NOT NULL DEFAULT 'MANUAL',
                last_seen_at TEXT,
                assigned_by TEXT NOT NULL,
                assigned_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(guild_id, player_id),
                FOREIGN KEY(alliance_id) REFERENCES alliances(id)
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_alliance_members_alliance ON alliance_members(guild_id, alliance_id, status)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_alliance_members_player ON alliance_members(guild_id, player_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_alliance_members_last_seen ON alliance_members(guild_id, last_seen_at)
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alliance_sync_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id TEXT NOT NULL,
                alliance_id INTEGER,
                provider TEXT NOT NULL,
                status TEXT NOT NULL,
                started_by TEXT,
                started_at TEXT NOT NULL,
                completed_at TEXT,
                total_members INTEGER DEFAULT 0,
                added_count INTEGER DEFAULT 0,
                removed_count INTEGER DEFAULT 0,
                rank_changed_count INTEGER DEFAULT 0,
                moved_count INTEGER DEFAULT 0,
                error_message TEXT
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_alliance_sync_runs_guild_started ON alliance_sync_runs(guild_id, started_at)
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alliance_rank_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id TEXT NOT NULL,
                alliance_id INTEGER NOT NULL,
                player_id TEXT NOT NULL,
                old_rank TEXT,
                new_rank TEXT NOT NULL,
                changed_by TEXT,
                source TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_alliance_rank_history_player ON alliance_rank_history(guild_id, player_id, created_at)
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alliance_member_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id TEXT NOT NULL,
                player_id TEXT NOT NULL,
                old_alliance_id INTEGER,
                new_alliance_id INTEGER,
                action TEXT NOT NULL,
                source TEXT NOT NULL,
                changed_by TEXT,
                created_at TEXT NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_alliance_member_history_player ON alliance_member_history(guild_id, player_id, created_at)
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alliance_api_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id TEXT NOT NULL,
                cache_key TEXT NOT NULL,
                payload_hash TEXT NOT NULL,
                cached_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                UNIQUE(guild_id, cache_key)
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_alliance_api_cache_key ON alliance_api_cache(guild_id, cache_key)
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alliance_audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id TEXT NOT NULL,
                actor_id TEXT NOT NULL,
                action TEXT NOT NULL,
                alliance_id INTEGER,
                player_id TEXT,
                result TEXT NOT NULL,
                metadata TEXT,
                created_at TEXT NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_alliance_audit_guild_created ON alliance_audit_logs(guild_id, created_at)
        """)
        
        conn.commit()


def init_language_table():
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_language_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                language TEXT NOT NULL DEFAULT 'ar',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(guild_id, user_id)
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_language_lookup
            ON user_language_preferences(guild_id, user_id)
        """)
        
        conn.commit()


def init_content_tables():
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS page_content_overrides (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id TEXT NOT NULL,
                page_key TEXT NOT NULL,
                block_key TEXT NOT NULL,
                language TEXT NOT NULL,
                custom_text TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'ACTIVE',
                updated_by TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(guild_id, page_key, block_key, language)
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_page_content_lookup
            ON page_content_overrides(guild_id, page_key, block_key, language)
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS page_content_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id TEXT NOT NULL,
                page_key TEXT NOT NULL,
                block_key TEXT NOT NULL,
                language TEXT NOT NULL,
                old_text TEXT,
                new_text TEXT,
                action TEXT NOT NULL,
                changed_by TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_page_content_history_lookup
            ON page_content_history(guild_id, page_key, block_key, created_at)
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS page_content_registry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                page_key TEXT NOT NULL,
                block_key TEXT NOT NULL,
                language TEXT NOT NULL,
                default_text TEXT NOT NULL,
                max_length INTEGER NOT NULL DEFAULT 500,
                editable INTEGER NOT NULL DEFAULT 1,
                content_type TEXT NOT NULL DEFAULT 'text',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(page_key, block_key, language)
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_page_content_registry_lookup
            ON page_content_registry(page_key, language)
        """)
        
        conn.commit()


def init_reminder_tables():
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS event_reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id TEXT NOT NULL,
                channel_id TEXT NOT NULL,
                event_name TEXT NOT NULL,
                event_time_local TEXT NOT NULL,
                event_time_utc TEXT NOT NULL,
                source_timezone TEXT NOT NULL,
                time_mode TEXT NOT NULL DEFAULT 'REAL_TIME',
                recurrence TEXT NOT NULL DEFAULT 'NONE',
                recurrence_pattern TEXT,
                role_id TEXT,
                created_by TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'ACTIVE',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_reminders_guild_time
            ON event_reminders(guild_id, event_time_utc, status)
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS event_reminder_offsets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reminder_id INTEGER NOT NULL,
                offset_minutes INTEGER NOT NULL,
                label TEXT,
                status TEXT NOT NULL DEFAULT 'ACTIVE',
                created_at TEXT NOT NULL,
                FOREIGN KEY(reminder_id) REFERENCES event_reminders(id) ON DELETE CASCADE
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS event_reminder_deliveries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reminder_id INTEGER NOT NULL,
                offset_id INTEGER,
                guild_id TEXT NOT NULL,
                channel_id TEXT NOT NULL,
                role_id TEXT,
                event_name TEXT NOT NULL,
                event_time_utc TEXT NOT NULL,
                delivery_time TEXT NOT NULL,
                status TEXT NOT NULL,
                error_message TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(reminder_id) REFERENCES event_reminders(id) ON DELETE CASCADE
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_deliveries_status
            ON event_reminder_deliveries(status, delivery_time)
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS event_reminder_audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id TEXT NOT NULL,
                actor_id TEXT NOT NULL,
                action TEXT NOT NULL,
                reminder_id INTEGER,
                result TEXT NOT NULL,
                risk_level TEXT NOT NULL,
                metadata TEXT,
                created_at TEXT NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reminder_time_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id TEXT NOT NULL UNIQUE,
                game_timezone TEXT NOT NULL DEFAULT 'UTC',
                real_timezone TEXT NOT NULL DEFAULT 'Asia/Riyadh',
                display_timezone TEXT NOT NULL DEFAULT 'Asia/Riyadh',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        conn.commit()


def init_player_id_service_tables():
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS player_id_owners (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id TEXT NOT NULL,
                discord_user_id TEXT NOT NULL,
                player_id TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'ACTIVE',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(guild_id, discord_user_id)
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_player_owners_guild_discord
            ON player_id_owners(guild_id, discord_user_id)
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS player_id_self_service_audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id TEXT NOT NULL,
                discord_user_id TEXT NOT NULL,
                action TEXT NOT NULL,
                old_player_id TEXT,
                new_player_id TEXT,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS player_id_panel_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id TEXT NOT NULL UNIQUE,
                panel_channel_id TEXT,
                require_confirmation INTEGER NOT NULL DEFAULT 1,
                allow_delete_own INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        conn.commit()


def init_feature_registry_tables():
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feature_registry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                feature_key TEXT NOT NULL UNIQUE,
                feature_name TEXT NOT NULL,
                version TEXT NOT NULL,
                enabled INTEGER NOT NULL DEFAULT 1,
                web_dashboard INTEGER NOT NULL DEFAULT 1,
                discord_panel INTEGER NOT NULL DEFAULT 0,
                category TEXT,
                manifest_hash TEXT NOT NULL,
                last_loaded_at TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feature_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id TEXT NOT NULL,
                feature_key TEXT NOT NULL,
                enabled INTEGER NOT NULL DEFAULT 1,
                settings_json TEXT,
                updated_by TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(guild_id, feature_key)
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_feature_settings_guild
            ON feature_settings(guild_id, feature_key)
        """)
        
        conn.commit()


def init_security_tables():
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id TEXT,
                actor_id TEXT,
                action TEXT NOT NULL,
                target TEXT,
                result TEXT NOT NULL,
                risk_level TEXT NOT NULL,
                metadata TEXT,
                created_at TEXT NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS security_incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id TEXT,
                incident_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                message TEXT NOT NULL,
                action_taken TEXT,
                created_at TEXT NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS command_rate_limits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                command_name TEXT NOT NULL,
                count INTEGER NOT NULL DEFAULT 0,
                window_start TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(guild_id, user_id, command_name)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS blocked_inputs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id TEXT,
                user_id TEXT,
                input_type TEXT NOT NULL,
                reason TEXT NOT NULL,
                sample_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_logs_guild_created ON audit_logs(guild_id, created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_security_incidents_severity_created ON security_incidents(severity, created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_command_rate_limits_lookup ON command_rate_limits(guild_id, user_id, command_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_blocked_inputs_guild_created ON blocked_inputs(guild_id, created_at)")
        
        conn.commit()


def save_audit_log(guild_id: str, actor_id: str, action: str, target: str, result: str, risk_level: str, metadata: str = None):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO audit_logs (guild_id, actor_id, action, target, result, risk_level, metadata, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (guild_id, actor_id, action, target, result, risk_level, metadata, now_iso())
        )
        conn.commit()


def get_audit_logs(guild_id: str, limit: int = 100) -> list:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM audit_logs WHERE guild_id = ? ORDER BY created_at DESC LIMIT ?",
            (guild_id, limit)
        )
        return [dict(row) for row in cursor.fetchall()]


def save_security_incident(guild_id: str, incident_type: str, severity: str, message: str, action_taken: str = None):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO security_incidents (guild_id, incident_type, severity, message, action_taken, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (guild_id, incident_type, severity, message, action_taken, now_iso())
        )
        conn.commit()


def get_security_incidents(severity: str = None, limit: int = 100) -> list:
    with get_db() as conn:
        cursor = conn.cursor()
        if severity:
            cursor.execute(
                "SELECT * FROM security_incidents WHERE severity = ? ORDER BY created_at DESC LIMIT ?",
                (severity, limit)
            )
        else:
            cursor.execute(
                "SELECT * FROM security_incidents ORDER BY created_at DESC LIMIT ?",
                (limit,)
            )
        return [dict(row) for row in cursor.fetchall()]


def check_command_rate_limit(guild_id: str, user_id: str, command_name: str, max_count: int, window_seconds: int) -> tuple[bool, int]:
    with get_db() as conn:
        cursor = conn.cursor()
        window_start = (datetime.utcnow() - timedelta(seconds=window_seconds)).isoformat()
        
        cursor.execute(
            """SELECT count FROM command_rate_limits 
               WHERE guild_id = ? AND user_id = ? AND command_name = ? AND window_start > ?""",
            (guild_id, user_id, command_name, window_start)
        )
        row = cursor.fetchone()
        
        if row:
            count = row[0]
            if count >= max_count:
                return False, count
        
        cursor.execute(
            """INSERT INTO command_rate_limits (guild_id, user_id, command_name, count, window_start, updated_at)
               VALUES (?, ?, ?, 1, ?, ?)
               ON CONFLICT(guild_id, user_id, command_name) DO UPDATE SET
               count = count + 1, updated_at = ?""",
            (guild_id, user_id, command_name, now_iso(), now_iso(), now_iso())
        )
        conn.commit()
        
        return True, count + 1 if row else 1


def block_input(guild_id: str, user_id: str, input_type: str, reason: str, sample_hash: str):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO blocked_inputs (guild_id, user_id, input_type, reason, sample_hash, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (guild_id, user_id, input_type, reason, sample_hash, now_iso())
        )
        conn.commit()


def is_input_blocked(guild_id: str, user_id: str, sample_hash: str) -> bool:
    with get_db() as conn:
        cursor = conn.cursor()
        cutoff = (datetime.utcnow() - timedelta(minutes=10)).isoformat()
        cursor.execute(
            """SELECT 1 FROM blocked_inputs 
               WHERE guild_id = ? AND user_id = ? AND sample_hash = ? AND created_at > ?""",
            (guild_id, user_id, sample_hash, cutoff)
        )
        return cursor.fetchone() is not None


def get_blocked_user_count(guild_id: str, user_id: str) -> int:
    with get_db() as conn:
        cursor = conn.cursor()
        cutoff = (datetime.utcnow() - timedelta(minutes=10)).isoformat()
        cursor.execute(
            "SELECT COUNT(*) FROM blocked_inputs WHERE guild_id = ? AND user_id = ? AND created_at > ?",
            (guild_id, user_id, cutoff)
        )
        return cursor.fetchone()[0]


def add_admin_user(guild_id: str, user_id: str, role_level: str, created_by: str) -> bool:
    now = datetime.utcnow().isoformat()
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO admin_users (guild_id, user_id, role_level, status, created_by, created_at, updated_at)
                   VALUES (?, ?, ?, 'ACTIVE', ?, ?, ?)""",
                (guild_id, user_id, role_level, created_by, now, now)
            )
            return True
    except sqlite3.IntegrityError:
        return False


def remove_admin_user(guild_id: str, user_id: str) -> bool:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM admin_users WHERE guild_id = ? AND user_id = ?",
            (guild_id, user_id)
        )
        if cursor.rowcount > 0:
            cursor.execute(
                "DELETE FROM admin_permissions WHERE guild_id = ? AND user_id = ?",
                (guild_id, user_id)
            )
            return True
        return False


def get_admin_user(guild_id: str, user_id: str) -> dict:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM admin_users WHERE guild_id = ? AND user_id = ? AND status = 'ACTIVE'",
            (guild_id, user_id)
        )
        row = cursor.fetchone()
        return dict(row) if row else None


def get_admins_by_guild(guild_id: str) -> list:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM admin_users WHERE guild_id = ? AND status = 'ACTIVE'",
            (guild_id,)
        )
        return [dict(row) for row in cursor.fetchall()]


def get_supervisors_by_guild(guild_id: str) -> list:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM admin_users WHERE guild_id = ? AND role_level = 'SUPERVISOR' AND status = 'ACTIVE'",
            (guild_id,)
        )
        return [dict(row) for row in cursor.fetchall()]


def set_admin_permission(guild_id: str, user_id: str, permission_key: str, enabled: bool, granted_by: str) -> bool:
    now = datetime.utcnow().isoformat()
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO admin_permissions (guild_id, user_id, permission_key, enabled, granted_by, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (guild_id, user_id, permission_key, 1 if enabled else 0, granted_by, now, now)
            )
            return True
    except sqlite3.IntegrityError:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE admin_permissions SET enabled = ?, updated_at = ? 
                   WHERE guild_id = ? AND user_id = ? AND permission_key = ?""",
                (1 if enabled else 0, now, guild_id, user_id, permission_key)
            )
            return True


def get_admin_permissions(guild_id: str, user_id: str) -> list:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT permission_key, enabled FROM admin_permissions WHERE guild_id = ? AND user_id = ?",
            (guild_id, user_id)
        )
        return {row['permission_key']: bool(row['enabled']) for row in cursor.fetchall()}


def has_admin_permission(guild_id: str, user_id: str, permission_key: str) -> bool:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT enabled FROM admin_permissions WHERE guild_id = ? AND user_id = ? AND permission_key = ?",
            (guild_id, user_id, permission_key)
        )
        row = cursor.fetchone()
        return bool(row['enabled']) if row else False


def remove_admin_permission(guild_id: str, user_id: str, permission_key: str) -> bool:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM admin_permissions WHERE guild_id = ? AND user_id = ? AND permission_key = ?",
            (guild_id, user_id, permission_key)
        )
        return cursor.rowcount > 0


def save_access_denial(guild_id: str, user_id: str, action: str, reason: str):
    now = datetime.utcnow().isoformat()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO access_denials (guild_id, user_id, action, reason, created_at) VALUES (?, ?, ?, ?, ?)",
            (guild_id, user_id, action, reason, now)
        )


def get_access_denial_count(user_id: str, minutes: int = 10) -> int:
    with get_db() as conn:
        cursor = conn.cursor()
        cutoff = (datetime.utcnow() - timedelta(minutes=minutes)).isoformat()
        cursor.execute(
            "SELECT COUNT(*) FROM access_denials WHERE user_id = ? AND created_at > ?",
            (user_id, cutoff)
        )
        return cursor.fetchone()[0]


def get_access_denials(user_id: str, limit: int = 100) -> list:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM access_denials WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
            (user_id, limit)
        )
        return [dict(row) for row in cursor.fetchall()]


init_database()
init_autopilot_tables()
init_alliance_tables()
init_language_table()
init_content_tables()
init_reminder_tables()
init_player_id_service_tables()
init_feature_registry_tables()
init_security_tables()
