#!/usr/bin/env python3
import os
import sys
import re
from pathlib import Path

FEATURES_DIR = Path(__file__).parent.parent / "src" / "features"
TEMPLATE_DIR = Path(__file__).parent.parent / "templates" / "feature_template"


def create_feature(feature_name: str):
    feature_key = feature_name.lower().replace(" ", "_")
    feature_dir = FEATURES_DIR / feature_key
    
    if feature_dir.exists():
        print(f"Error: Feature '{feature_key}' already exists at {feature_dir}")
        sys.exit(1)
    
    feature_dir.mkdir(parents=True, exist_ok=True)
    
    manifest_content = f'''FEATURE_MANIFEST = {{
    "key": "{feature_key}",
    "name": {{
        "ar": "{feature_name}",
        "en": "{feature_name}"
    }},
    "description": {{
        "ar": "وصف الميزة.",
        "en": "Feature description."
    }},
    "icon": "📦",
    "category": "general",
    "version": "1.0.0",
    "enabled": True,
    "web_dashboard": True,
    "discord_panel": False,
    "requires_auth": True,
    "required_permissions": [],
    "admin_permissions": [],
    "routes": [
        {{
            "path": "/{feature_key}",
            "label_key": "features.{feature_key}.title",
            "permission": None,
            "component": "{feature_key.title().replace('_', '')}Page",
            "show_in_sidebar": True,
            "order": 100
        }}
    ],
    "api_prefix": "/api/v1/{feature_key}",
    "health_check": None,
    "overview_cards": [],
    "settings_sections": [],
    "audit_events": []
}}
'''
    
    with open(feature_dir / "feature_manifest.py", "w") as f:
        f.write(manifest_content)
    
    service_content = f'''from typing import Dict, Optional, List

class {feature_key.title().replace('_', '')}Service:
    def __init__(self):
        self.feature_key = "{feature_key}"
    
    def health_check(self) -> Dict:
        return {{"status": "healthy", "feature": self.feature_key}}
    
    def get_stats(self) -> Dict:
        return {{"total": 0}}

{feature_key}_service = {feature_key.title().replace('_', '')}Service()
'''
    
    with open(feature_dir / "service.py", "w") as f:
        f.write(service_content)
    
    routes_content = f'''from fastapi import APIRouter, Depends
from typing import Dict, List

router = APIRouter()

@router.get("/health")
async def health() -> Dict:
    from src.services.{feature_key}.service import {feature_key}_service
    return {feature_key}_service.health_check()

@router.get("/stats")
async def stats() -> Dict:
    from src.services.{feature_key}.service import {feature_key}_service
    return {feature_key}_service.get_stats()
'''
    
    with open(feature_dir / "routes.py", "w") as f:
        f.write(routes_content)
    
    permissions_content = f'''REQUIRED_PERMISSIONS = []
ADMIN_PERMISSIONS = []
'''
    
    with open(feature_dir / "permissions.py", "w") as f:
        f.write(permissions_content)
    
    i18n_content = f'''ar = {{
    "features.{feature_key}.title": "{feature_name}",
    "features.{feature_key}.description": "وصف الميزة",
}}

en = {{
    "features.{feature_key}.title": "{feature_name}",
    "features.{feature_key}.description": "Feature description",
}}
'''
    
    with open(feature_dir / "i18n.py", "w") as f:
        f.write(i18n_content)
    
    health_content = f'''def {feature_key}_health_check() -> Dict:
    from src.services.{feature_key}.service import {feature_key}_service
    return {feature_key}_service.health_check()
'''
    
    with open(feature_dir / "health.py", "w") as f:
        f.write(health_content)
    
    print(f"Feature '{feature_key}' created successfully at {feature_dir}")
    print(f"Files created:")
    print(f"  - feature_manifest.py")
    print(f"  - service.py")
    print(f"  - routes.py")
    print(f"  - permissions.py")
    print(f"  - i18n.py")
    print(f"  - health.py")
    print()
    print("Next steps:")
    print(f"  1. Edit src/features/{feature_key}/feature_manifest.py")
    print(f"  2. Implement your feature logic in service.py")
    print(f"  3. Add API routes in routes.py")
    print(f"  4. Add translations in i18n.py")
    print(f"  5. Reload features: restart the bot")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python create_feature.py <feature_name>")
        print("Example: python create_feature.py rewards")
        sys.exit(1)
    
    feature_name = sys.argv[1]
    create_feature(feature_name)
