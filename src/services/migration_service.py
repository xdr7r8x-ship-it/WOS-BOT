from typing import Callable, Optional

from database import save_migration, get_migrations, migration_exists


class MigrationService:
    def __init__(self):
        self.migrations: dict[str, Callable] = {}
        
    def register(self, migration_id: str, rollback_sql: Optional[str] = None):
        def decorator(func: Callable):
            self.migrations[migration_id] = (func, rollback_sql)
            return func
        return decorator
    
    def run_migration(self, migration_id: str) -> tuple[bool, str]:
        if migration_exists(migration_id):
            return True, "Already applied"
        
        if migration_id not in self.migrations:
            return False, f"Migration {migration_id} not found"
        
        func, rollback_sql = self.migrations[migration_id]
        
        try:
            func()
            save_migration(migration_id, rollback_sql)
            return True, "Applied successfully"
        except Exception as e:
            return False, str(e)
    
    def run_all_pending(self) -> list[dict]:
        results = []
        for migration_id in self.migrations:
            if not migration_exists(migration_id):
                success, msg = self.run_migration(migration_id)
                results.append({
                    "id": migration_id,
                    "success": success,
                    "message": msg
                })
        return results
    
    def get_applied(self) -> list:
        return get_migrations()


migration_service = MigrationService()
