FEATURE_MANIFEST = {
    "key": "reminders",
    "name": {
        "ar": "التذكيرات",
        "en": "Reminders"
    },
    "description": {
        "ar": "إدارة تذكيرات الدب والأحداث والتذكيرات المخصصة مع دعم GAME_TIME و REAL_TIME.",
        "en": "Manage Bear Trap, event, and custom reminders with GAME_TIME and REAL_TIME support."
    },
    "icon": "⏰",
    "category": "operations",
    "version": "1.0.0",
    "enabled": True,
    "web_dashboard": True,
    "discord_panel": True,
    "requires_auth": True,
    "required_permissions": [],
    "admin_permissions": [
        "REMINDERS_CREATE",
        "REMINDERS_UPDATE",
        "REMINDERS_DISABLE",
        "REMINDERS_SEND_TEST",
        "REMINDERS_SETTINGS"
    ],
    "routes": [
        {
            "path": "/reminders",
            "label_key": "features.reminders.title",
            "permission": None,
            "component": "RemindersPage",
            "show_in_sidebar": True,
            "order": 70
        }
    ],
    "api_prefix": "/api/v1/reminders",
    "health_check": "reminders_health_check",
    "overview_cards": [
        {
            "key": "upcoming_reminders",
            "label_key": "features.reminders.upcoming",
            "metric_endpoint": "/api/v1/reminders/stats",
            "permission": None
        }
    ],
    "settings_sections": [
        {
            "key": "reminder_time_settings",
            "label_key": "features.reminders.time_settings",
            "permission": "REMINDERS_SETTINGS"
        }
    ],
    "audit_events": [
        "REMINDER_CREATED",
        "REMINDER_UPDATED",
        "REMINDER_DELIVERED",
        "REMINDER_DELETED"
    ]
}
