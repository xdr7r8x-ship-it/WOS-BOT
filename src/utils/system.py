import os
import sys
import psutil
import platform
from pathlib import Path


def get_python_version() -> str:
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"


def get_platform() -> str:
    return platform.platform()


def get_cpu_count() -> int:
    return os.cpu_count() or 1


def get_memory_info() -> dict:
    mem = psutil.virtual_memory()
    return {
        "total": mem.total,
        "available": mem.available,
        "percent": mem.percent,
        "used": mem.used,
        "free": mem.free,
    }


def get_disk_info(path: str = "/") -> dict:
    disk = psutil.disk_usage(path)
    return {
        "total": disk.total,
        "used": disk.used,
        "free": disk.free,
        "percent": disk.percent,
    }


def get_process_memory() -> int:
    process = psutil.Process()
    return process.memory_info().rss


def get_uptime() -> float:
    boot_time = psutil.boot_time()
    return psutil.time.time() - boot_time


def get_disk_usage_percent(path: str = "/") -> float:
    return psutil.disk_usage(path).percent


def get_memory_usage_percent() -> float:
    return psutil.virtual_memory().percent


def ensure_directory(path: Path) -> bool:
    try:
        path.mkdir(parents=True, exist_ok=True)
        return True
    except Exception:
        return False


def get_directory_size(path: Path) -> int:
    total = 0
    try:
        for entry in path.rglob("*"):
            if entry.is_file():
                total += entry.stat().st_size
    except Exception:
        pass
    return total


def is_directory_writable(path: Path) -> bool:
    try:
        test_file = path / ".write_test"
        test_file.touch()
        test_file.unlink()
        return True
    except Exception:
        return False
