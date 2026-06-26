FEATURE_MANIFEST = {
    "key": "alliance",
    "name": {
        "ar": "التحالفات",
        "en": "Alliances"
    },
    "description": {
        "ar": "إدارة التحالفات والأعضاء والرتب مع مزامنة API.",
        "en": "Manage alliances, members, and ranks with API sync."
    },
    "icon": "🏰",
    "category": "management",
    "version": "1.0.0",
    "enabled": True,
    "web_dashboard": True,
    "discord_panel": True,
    "requires_auth": True,
    "required_permissions": [
        "ALLIANCE_VIEW"
    ],
    "admin_permissions": [
        "ALLIANCE_VIEW", "ALLIANCE_CREATE", "ALLIANCE_UPDATE", "ALLIANCE_DISABLE",
        "ALLIANCE_MEMBERS_VIEW", "ALLIANCE_MEMBER_ASSIGN", "ALLIANCE_MEMBER_REMOVE", "ALLIANCE_MEMBER_RANK_UPDATE",
        "ALLIANCE_STATS_VIEW", "ALLIANCE_AUDIT_VIEW",
        "ALLIANCE_API_VIEW", "ALLIANCE_API_CONFIG", "ALLIANCE_API_SYNC", "ALLIANCE_API_AUTO_SYNC_TOGGLE", "ALLIANCE_API_HEALTH"
    ],
    "routes": [
        {
            "path": "/alliances",
            "label_key": "features.alliance.title",
            "permission": "ALLIANCE_VIEW",
            "component": "AlliancesPage",
            "show_in_sidebar": True,
            "order": 30
        }
    ],
    "api_prefix": "/api/v1/alliances",
    "health_check": "alliance_health_check",
    "overview_cards": [
        {
            "key": "total_alliances",
            "label_key": "features.alliance.total",
            "metric_endpoint": "/api/v1/alliances/stats",
            "permission": "ALLIANCE_VIEW"
        }
    ],
    "settings_sections": [
        {
            "key": "alliance_api_settings",
            "label_key": "features.alliance.api_settings",
            "permission": "ALLIANCE_API_CONFIG"
        }
    ],
    "audit_events": [
        "ALLIANCE_CREATED",
        "ALLIANCE_UPDATED",
        "ALLIANCE_DISABLED",
        "ALLIANCE_MEMBER_ADDED",
        "ALLIANCE_MEMBER_REMOVED",
        "ALLIANCE_RANK_CHANGED"
    ]
}
