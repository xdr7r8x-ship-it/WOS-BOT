from typing import List, Set

WEB_PERMISSIONS = {
    "WEB_DASHBOARD_VIEW",
    "WEB_SYSTEM_VIEW",
    "WEB_SYSTEM_CONTROL",
    "WEB_GIFT_CODES_VIEW",
    "WEB_GIFT_CODES_MANAGE",
    "WEB_PLAYERS_VIEW",
    "WEB_PLAYERS_MANAGE",
    "WEB_PLAYER_PANEL_MANAGE",
    "WEB_ALLIANCE_VIEW",
    "WEB_ALLIANCE_MANAGE",
    "WEB_ALLIANCE_API_MANAGE",
    "WEB_REMINDERS_VIEW",
    "WEB_REMINDERS_MANAGE",
    "WEB_CONTENT_VIEW",
    "WEB_CONTENT_EDIT",
    "WEB_ADMINS_VIEW",
    "WEB_ADMINS_MANAGE",
    "WEB_SECURITY_VIEW",
    "WEB_SECURITY_MANAGE",
    "WEB_BACKUP_VIEW",
    "WEB_BACKUP_CREATE",
    "WEB_ROLLBACK_EXECUTE",
    "WEB_UPDATES_VIEW",
    "WEB_UPDATES_APPLY",
    "WEB_AUDIT_VIEW",
}

ROLE_PERMISSION_MAP = {
    "OWNER": WEB_PERMISSIONS,
    "ADMIN": {
        "WEB_DASHBOARD_VIEW",
        "WEB_GIFT_CODES_VIEW",
        "WEB_GIFT_CODES_MANAGE",
        "WEB_PLAYERS_VIEW",
        "WEB_PLAYERS_MANAGE",
        "WEB_PLAYER_PANEL_MANAGE",
        "WEB_ALLIANCE_VIEW",
        "WEB_ALLIANCE_MANAGE",
        "WEB_ALLIANCE_API_MANAGE",
        "WEB_REMINDERS_VIEW",
        "WEB_REMINDERS_MANAGE",
        "WEB_CONTENT_VIEW",
        "WEB_CONTENT_EDIT",
        "WEB_ADMINS_VIEW",
        "WEB_SECURITY_VIEW",
        "WEB_SECURITY_MANAGE",
        "WEB_BACKUP_VIEW",
        "WEB_BACKUP_CREATE",
        "WEB_AUDIT_VIEW",
    },
    "SUPERVISOR": {
        "WEB_DASHBOARD_VIEW",
        "WEB_GIFT_CODES_VIEW",
        "WEB_PLAYERS_VIEW",
        "WEB_ALLIANCE_VIEW",
        "WEB_REMINDERS_VIEW",
        "WEB_CONTENT_VIEW",
        "WEB_SECURITY_VIEW",
        "WEB_BACKUP_VIEW",
        "WEB_AUDIT_VIEW",
    },
    "MEMBER": set(),
}


def get_role_permissions(role_level: str) -> Set[str]:
    if role_level == "OWNER":
        return WEB_PERMISSIONS
    return ROLE_PERMISSION_MAP.get(role_level, set())


def has_permission(role_level: str, permission: str) -> bool:
    return permission in get_role_permissions(role_level)


def has_any_permission(role_level: str, permissions: List[str]) -> bool:
    user_perms = get_role_permissions(role_level)
    return any(p in user_perms for p in permissions)


def has_all_permissions(role_level: str, permissions: List[str]) -> bool:
    user_perms = get_role_permissions(role_level)
    return all(p in user_perms for p in permissions)
