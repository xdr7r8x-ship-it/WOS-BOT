FEATURE_MANIFEST = {
    "key": "gift_codes",
    "name": {
        "ar": "أكواد الهدايا",
        "en": "Gift Codes"
    },
    "description": {
        "ar": "إدارة أكواد الهدايا واستردادها تلقائيًا.",
        "en": "Manage gift codes and redeem them automatically."
    },
    "icon": "🎁",
    "category": "operations",
    "version": "1.0.0",
    "enabled": True,
    "web_dashboard": True,
    "discord_panel": True,
    "requires_auth": True,
    "required_permissions": [
        "CODES_REDEEM"
    ],
    "admin_permissions": [
        "CODES_REDEEM",
        "CODES_STATUS",
        "CODES_QUEUE_VIEW"
    ],
    "routes": [
        {
            "path": "/codes",
            "label_key": "features.gift_codes.title",
            "permission": "CODES_REDEEM",
            "component": "GiftCodesPage",
            "show_in_sidebar": True,
            "order": 10
        }
    ],
    "api_prefix": "/api/v1/gift-codes",
    "health_check": "gift_codes_health_check",
    "overview_cards": [
        {
            "key": "pending_codes",
            "label_key": "features.gift_codes.pending",
            "metric_endpoint": "/api/v1/gift-codes/stats",
            "permission": "CODES_STATUS"
        }
    ],
    "settings_sections": [],
    "audit_events": [
        "CODE_REDEEMED",
        "CODE_FAILED",
        "CODE_RETRY"
    ]
}
