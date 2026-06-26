FEATURE_MANIFEST = {
    "key": "security",
    "name": {
        "ar": "الأمان",
        "en": "Security"
    },
    "description": {
        "ar": "إدارة الأمان والحماية.",
        "en": "Security management and protection."
    },
    "icon": "🛡️",
    "category": "system",
    "version": "1.0.0",
    "enabled": True,
    "web_dashboard": True,
    "discord_panel": True,
    "requires_auth": True,
    "required_permissions": [
        "SECURITY_SCAN"
    ],
    "admin_permissions": [
        "SECURITY_SCAN",
        "SECURITY_AUDIT_VIEW",
        "SECURITY_INCIDENTS_VIEW",
        "SECURITY_BLOCKED_VIEW"
    ],
    "routes": [
        {
            "path": "/security",
            "label_key": "features.security.title",
            "permission": "SECURITY_SCAN",
            "component": "SecurityPage",
            "show_in_sidebar": True,
            "order": 40
        }
    ],
    "api_prefix": "/api/v1/security",
    "health_check": "security_health_check",
    "overview_cards": [
        {
            "key": "blocked_count",
            "label_key": "features.security.blocked",
            "metric_endpoint": "/api/v1/security/stats",
            "permission": "SECURITY_BLOCKED_VIEW"
        }
    ],
    "settings_sections": [],
    "audit_events": [
        "SECURITY_SCAN_PERFORMED",
        "SECURITY_INCIDENT_DETECTED",
        "ACCESS_DENIED",
        "INPUT_BLOCKED"
    ]
}
