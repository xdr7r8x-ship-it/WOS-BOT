import asyncio
import logging
from pathlib import Path
from datetime import datetime

from src.utils.config import get_config


class LogRotationService:
    def __init__(self):
        self.config = get_config()
        self._running = False
        self.logger = logging.getLogger(__name__)
    
    async def start(self):
        self._running = True
        self._ensure_logs_dir()
        
        while self._running:
            try:
                await self.rotate_logs()
                await asyncio.sleep(self.config.LOG_ROTATION_INTERVAL)
            except Exception as e:
                self.logger.error(f"Log rotation error: {e}")
                await asyncio.sleep(300)
    
    def stop(self):
        self._running = False
    
    def _ensure_logs_dir(self):
        logs_dir = Path(self.config.LOGS_DIR)
        logs_dir.mkdir(parents=True, exist_ok=True)
    
    async def rotate_logs(self):
        logs_dir = Path(self.config.LOGS_DIR)
        max_size_bytes = self.config.MAX_LOG_SIZE_MB * 1024 * 1024
        max_files = self.config.MAX_LOG_FILES
        
        rotated = []
        
        for log_file in logs_dir.glob("*.log"):
            try:
                size = log_file.stat().st_size
                if size > max_size_bytes:
                    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
                    archive_name = f"{log_file.stem}_{timestamp}.log"
                    archive_path = log_file.parent / archive_name
                    
                    log_file.rename(archive_path)
                    rotated.append(str(archive_path.name))
                    
                    log_file.touch()
            
            except Exception as e:
                self.logger.warning(f"Failed to rotate {log_file}: {e}")
        
        if rotated:
            self._cleanup_old_logs(logs_dir, max_files)
        
        return rotated
    
    def _cleanup_old_logs(self, logs_dir: Path, max_files: int):
        try:
            logs = sorted(logs_dir.glob("*.log"), key=lambda p: p.stat().st_mtime)
            
            for old_log in logs[:-max_files]:
                if old_log.stem.endswith("_"):
                    continue
                old_log.unlink()
        
        except Exception as e:
            self.logger.warning(f"Failed to cleanup old logs: {e}")


log_rotation_service = LogRotationService()
