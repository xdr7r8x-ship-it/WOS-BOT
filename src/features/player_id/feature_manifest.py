FEATURE_MANIFEST = {
    "key": "player_id",
    "name": {
        "ar": "Player ID",
        "en": "Player ID"
    },
    "description": {
        "ar": "لوحة Player ID الذاتية.",
        "en": "Self-service Player ID panel."
    },
    "icon": "🔑",
    "category": "self_service",
    "version": "1.0.0",
    "enabled": True,
    "web_dashboard": True,
    "discord_panel": True,
    "requires_auth": True,
    "required_permissions": [],
    "admin_permissions": [
        "PLAYER_ID_MANAGE"
    ],
    "routes": [
        {
            "path": "/player-id",
            "label_key": "features.player_id.title",
            "permission": None,
            "component": "PlayerIDPage",
            "show_in_sidebar": True,
            "order": 60
        }
    ],
    "api_prefix": "/api/v1/player-id",
    "health_check": None,
    "overview_cards": [
        {
            "key": "registered_count",
            "label_key": "features.player_id.registered",
            "metric_endpoint": "/api/v1/player-id/stats",
            "permission": None
        }
    ],
    "settings_sections": [],
    "audit_events": [
        "PLAYER_ID_REGISTERED",
        "PLAYER_ID_UPDATED",
        "PLAYER_ID_DELETED",
        "PLAYER_ID_CLEANUP"
    ]
}
