FEATURE_MANIFEST = {
    "key": "players",
    "name": {
        "ar": "اللاعبين",
        "en": "Players"
    },
    "description": {
        "ar": "إدارة قائمة اللاعبين المسجلين.",
        "en": "Manage registered players list."
    },
    "icon": "👥",
    "category": "management",
    "version": "1.0.0",
    "enabled": True,
    "web_dashboard": True,
    "discord_panel": True,
    "requires_auth": True,
    "required_permissions": [
        "PLAYERS_VIEW"
    ],
    "admin_permissions": [
        "PLAYERS_VIEW",
        "PLAYERS_DISABLE"
    ],
    "routes": [
        {
            "path": "/players",
            "label_key": "features.players.title",
            "permission": "PLAYERS_VIEW",
            "component": "PlayersPage",
            "show_in_sidebar": True,
            "order": 20
        }
    ],
    "api_prefix": "/api/v1/players",
    "health_check": None,
    "overview_cards": [
        {
            "key": "total_players",
            "label_key": "features.players.total",
            "metric_endpoint": "/api/v1/players/stats",
            "permission": "PLAYERS_VIEW"
        }
    ],
    "settings_sections": [],
    "audit_events": [
        "PLAYER_REGISTERED",
        "PLAYER_DISABLED"
    ]
}
