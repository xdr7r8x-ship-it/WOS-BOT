FEATURE_MANIFEST = {
    "key": "page_content",
    "name": {
        "ar": "تحرير النصوص",
        "en": "Page Content"
    },
    "description": {
        "ar": "تحرير نصوص الصفحات وتخصيصها.",
        "en": "Edit and customize page texts."
    },
    "icon": "📝",
    "category": "settings",
    "version": "1.0.0",
    "enabled": True,
    "web_dashboard": True,
    "discord_panel": True,
    "requires_auth": True,
    "required_permissions": [],
    "admin_permissions": [
        "CONTENT_VIEW",
        "CONTENT_EDIT",
        "CONTENT_RESET",
        "CONTENT_AUDIT_VIEW"
    ],
    "routes": [
        {
            "path": "/content",
            "label_key": "features.page_content.title",
            "permission": "CONTENT_EDIT",
            "component": "ContentPage",
            "show_in_sidebar": True,
            "order": 80
        }
    ],
    "api_prefix": "/api/v1/content",
    "health_check": None,
    "overview_cards": [],
    "settings_sections": [
        {
            "key": "page_content_settings",
            "label_key": "features.page_content.settings",
            "permission": "CONTENT_EDIT"
        }
    ],
    "audit_events": [
        "PAGE_CONTENT_UPDATED",
        "PAGE_CONTENT_RESET",
        "CONTENT_SECURITY_REJECTED"
    ]
}
