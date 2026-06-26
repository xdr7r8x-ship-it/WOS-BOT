import re
from pathlib import Path
from typing import Optional

VERSION_FILE = Path("VERSION")

VERSION_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")


def read_version() -> Optional[str]:
    try:
        if VERSION_FILE.exists():
            version = VERSION_FILE.read_text().strip()
            if VERSION_PATTERN.match(version):
                return version
    except Exception:
        pass
    return None


def validate_version(version: str) -> bool:
    return bool(VERSION_PATTERN.match(version))


def compare_versions(v1: str, v2: str) -> int:
    def parse(v):
        return [int(x) for x in v.split(".")] if validate_version(v) else [0, 0, 0]
    
    parts1 = parse(v1)
    parts2 = parse(v2)
    
    for p1, p2 in zip(parts1, parts2):
        if p1 > p2:
            return 1
        elif p1 < p2:
            return -1
    return 0


def is_downgrade(current: str, target: str) -> bool:
    return compare_versions(current, target) > 0


def get_version_type(current: str, target: str) -> str:
    def parse(v):
        return [int(x) for x in v.split(".")] if validate_version(v) else [0, 0, 0]
    
    parts1 = parse(current)
    parts2 = parse(target)
    
    if parts1[0] != parts2[0]:
        return "MAJOR"
    elif parts1[1] != parts2[1]:
        return "MINOR"
    elif parts1[2] != parts2[2]:
        return "PATCH"
    return "SAME"
