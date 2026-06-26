FEATURE_MANIFEST = {
    "key": "autopilot",
    "name": {
        "ar": "النظام",
        "en": "System"
    },
    "description": {
        "ar": "إدارة النظام والتشخيص والتحديثات.",
        "en": "System management, diagnostics, and updates."
    },
    "icon": "⚙️",
    "category": "system",
    "version": "1.0.0",
    "enabled": True,
    "web_dashboard": True,
    "discord_panel": True,
    "requires_auth": True,
    "required_permissions": [
        "SYSTEM_VIEW"
    ],
    "admin_permissions": [
        "SYSTEM_VIEW", "SYSTEM_DIAGNOSTICS", "SYSTEM_INTEGRITY",
        "BACKUP_CREATE", "BACKUP_LIST", "ROLLBACK_EXECUTE",
        "UPDATES_CHECK", "UPDATES_PLAN", "UPDATES_APPLY",
        "MAINTENANCE_CLEANUP", "MAINTENANCE_RETRY", "MAINTENANCE_LOGS_VIEW"
    ],
    "routes": [
        {
            "path": "/system",
            "label_key": "features.autopilot.system",
            "permission": "SYSTEM_VIEW",
            "component": "SystemPage",
            "show_in_sidebar": True,
            "order": 50
        },
        {
            "path": "/backups",
            "label_key": "features.autopilot.backups",
            "permission": "BACKUP_LIST",
            "component": "BackupsPage",
            "show_in_sidebar": True,
            "order": 51
        },
        {
            "path": "/updates",
            "label_key": "features.autopilot.updates",
            "permission": "UPDATES_CHECK",
            "component": "UpdatesPage",
            "show_in_sidebar": True,
            "order": 52
        }
    ],
    "api_prefix": "/api/v1/system",
    "health_check": "system_health_check",
    "overview_cards": [
        {
            "key": "system_status",
            "label_key": "features.autopilot.status",
            "metric_endpoint": "/api/v1/system/status",
            "permission": "SYSTEM_VIEW"
        }
    ],
    "settings_sections": [],
    "audit_events": [
        "BACKUP_CREATED",
        "BACKUP_RESTORED",
        "UPDATE_APPLIED",
        "SYSTEM_DIAGNOSTICS_RUN"
    ]
}
