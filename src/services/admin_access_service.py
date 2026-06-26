import os
import logging
from typing import Optional
from database import (
    add_admin_user, remove_admin_user, get_admin_user,
    get_admins_by_guild, get_supervisors_by_guild,
    set_admin_permission, get_admin_permissions,
    has_admin_permission, remove_admin_permission,
    save_access_denial, get_access_denial_count,
    save_audit_log, save_security_incident,
)
from src.utils.rbac import (
    OWNER_LEVEL, ADMIN_LEVEL, SUPERVISOR_LEVEL,
    ROLE_LEVELS, ALL_PERMISSIONS, OWNER_IMPLICIT_PERMISSIONS,
    ADMIN_DEFAULT_PERMISSIONS, SUPERVISOR_DEFAULT_PERMISSIONS,
)

logger = logging.getLogger(__name__)


def get_owner_ids() -> list:
    owner_ids_str = os.getenv("BOT_OWNER_IDS", "")
    if not owner_ids_str:
        return []
    return [oid.strip() for oid in owner_ids_str.split(",") if oid.strip()]


def is_owner(user_id: str) -> bool:
    return user_id in get_owner_ids()


def get_role_level(guild_id: str, user_id: str) -> Optional[str]:
    if is_owner(user_id):
        return OWNER_LEVEL
    admin = get_admin_user(guild_id, user_id)
    return admin.get("role_level") if admin else None


def is_authorized(guild_id: str, user_id: str) -> bool:
    if is_owner(user_id):
        return True
    admin = get_admin_user(guild_id, user_id)
    return admin is not None and admin.get("status") == "ACTIVE"


def check_permission(guild_id: str, user_id: str, permission_key: str) -> bool:
    if is_owner(user_id):
        return True
    if permission_key == "PANEL_VIEW":
        return is_authorized(guild_id, user_id)
    return has_admin_permission(guild_id, user_id, permission_key)


def check_permission_or_die(guild_id: str, user_id: str, permission_key: str) -> tuple[bool, str]:
    if check_permission(guild_id, user_id, permission_key):
        return True, "OK"
    admin = get_admin_user(guild_id, user_id)
    role = admin.get("role_level") if admin else "NONE"
    return False, f"Permission denied: {permission_key} (role: {role})"


def add_admin(guild_id: str, target_user_id: str, created_by: str) -> tuple[bool, str]:
    if is_owner(target_user_id):
        return False, "Cannot add owner as admin"
    if get_admin_user(guild_id, target_user_id):
        return False, "User is already an admin"
    if not add_admin_user(guild_id, target_user_id, ADMIN_LEVEL, created_by):
        return False, "Failed to add admin"
    for perm in ADMIN_DEFAULT_PERMISSIONS:
        set_admin_permission(guild_id, target_user_id, perm, True, created_by)
    save_audit_log(guild_id, created_by, "ADMIN_CREATED", target_user_id, "SUCCESS", "HIGH")
    return True, "Admin added successfully"


def add_supervisor(guild_id: str, target_user_id: str, created_by: str) -> tuple[bool, str]:
    if is_owner(target_user_id):
        return False, "Cannot add owner as supervisor"
    if get_admin_user(guild_id, target_user_id):
        return False, "User already exists"
    if not add_admin_user(guild_id, target_user_id, SUPERVISOR_LEVEL, created_by):
        return False, "Failed to add supervisor"
    for perm in SUPERVISOR_DEFAULT_PERMISSIONS:
        set_admin_permission(guild_id, target_user_id, perm, True, created_by)
    save_audit_log(guild_id, created_by, "SUPERVISOR_CREATED", target_user_id, "SUCCESS", "MEDIUM")
    return True, "Supervisor added successfully"


def remove_admin(guild_id: str, target_user_id: str, removed_by: str) -> tuple[bool, str]:
    if is_owner(target_user_id):
        return False, "Cannot remove owner"
    admin = get_admin_user(guild_id, target_user_id)
    if not admin:
        return False, "Admin not found"
    if not remove_admin_user(guild_id, target_user_id):
        return False, "Failed to remove admin"
    action = f"{admin.get('role_level')}_DELETED".upper()
    save_audit_log(guild_id, removed_by, action, target_user_id, "SUCCESS", "HIGH")
    return True, "Admin removed successfully"


def update_permission(guild_id: str, target_user_id: str, permission_key: str, enabled: bool, updated_by: str) -> tuple[bool, str]:
    if is_owner(target_user_id):
        return False, "Cannot modify owner permissions"
    if target_user_id == updated_by and not is_owner(updated_by):
        save_audit_log(guild_id, updated_by, "SELF_PERMISSION_EDIT_BLOCKED", permission_key, "BLOCKED", "HIGH")
        return False, "Cannot modify your own permissions"
    if not set_admin_permission(guild_id, target_user_id, permission_key, enabled, updated_by):
        return False, "Failed to update permission"
    save_audit_log(guild_id, updated_by, "PERMISSION_UPDATED", f"{target_user_id}:{permission_key}", "SUCCESS", "MEDIUM")
    return True, "Permission updated"


def get_user_permissions(guild_id: str, user_id: str) -> dict:
    if is_owner(user_id):
        return {perm: True for perm in OWNER_IMPLICIT_PERMISSIONS}
    return get_admin_permissions(guild_id, user_id)


def record_access_denial(guild_id: str, user_id: str, action: str, reason: str):
    save_access_denial(guild_id, user_id, action, reason)
    denial_count = get_access_denial_count(user_id, 10)
    if denial_count >= 3:
        save_security_incident(
            guild_id, "UNAUTHORIZED_ACCESS_ATTEMPT",
            "HIGH" if denial_count >= 5 else "MEDIUM",
            f"User {user_id} denied {action} {denial_count} times in 10 minutes",
            "User may be blocked"
        )
    save_audit_log(guild_id, user_id, "WOS_ACCESS_DENIED", action, "BLOCKED", "LOW", reason)


def authorize_and_log(guild_id: str, user_id: str, action: str) -> bool:
    if is_authorized(guild_id, user_id):
        save_audit_log(guild_id, user_id, "WOS_ACCESS_GRANTED", action, "SUCCESS", "LOW")
        return True
    record_access_denial(guild_id, user_id, action, "Not authorized")
    return False


def can_manage_role(actor_id: str, actor_role: str, target_role: str) -> bool:
    if is_owner(actor_id):
        return True
    actor_level = ROLE_LEVELS.get(actor_role, 0)
    target_level = ROLE_LEVELS.get(target_role, 0)
    if target_level >= actor_level:
        return False
    if actor_role == ADMIN_LEVEL and target_role == ADMIN_LEVEL:
        return has_admin_permission(None, actor_id, "ADMINS_UPDATE")
    if actor_role == SUPERVISOR_LEVEL:
        return False
    return False


def get_all_admins(guild_id: str) -> list:
    return get_admins_by_guild(guild_id)


def get_all_supervisors(guild_id: str) -> list:
    return get_supervisors_by_guild(guild_id)


def validate_owner_ids_config() -> tuple[bool, str]:
    owner_ids = get_owner_ids()
    if not owner_ids:
        return False, "BOT_OWNER_IDS is not configured. Admin system disabled."
    return True, "OK"
