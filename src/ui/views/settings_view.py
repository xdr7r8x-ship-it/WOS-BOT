import discord
from discord import ui

from src.services.admin_access_service import (
    is_owner, check_permission,
    get_all_admins, get_all_supervisors,
    add_admin, add_supervisor, remove_admin,
    get_user_permissions, get_owner_ids
)
from src.ui.components.embeds import create_section_embed, create_success_embed, create_error_embed, create_unauthorized_embed
from src.ui.modals.add_admin_modal import AddAdminModal
from src.ui.modals.add_supervisor_modal import AddSupervisorModal


class SettingsView(ui.View):
    def __init__(self, user_id: str, guild_id: str):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.guild_id = guild_id
        self.add_buttons()

    def add_buttons(self):
        if is_owner(self.user_id):
            self.add_item(ui.Button(
                style=discord.ButtonStyle.primary,
                label="👑 إعدادات المالك",
                custom_id="wos:settings:owner",
                row=0
            ))
            self.add_item(ui.Button(
                style=discord.ButtonStyle.danger,
                label="🛡️ إدارة الأدمن",
                custom_id="wos:settings:admins",
                row=1
            ))
            self.add_item(ui.Button(
                style=discord.ButtonStyle.danger,
                label="👮 إدارة المشرفين",
                custom_id="wos:settings:supervisors",
                row=1
            ))
            self.add_item(ui.Button(
                style=discord.ButtonStyle.secondary,
                label="🔐 إدارة الصلاحيات",
                custom_id="wos:settings:permissions",
                row=2
            ))
        elif check_permission(self.guild_id, self.user_id, "SETTINGS_VIEW"):
            self.add_item(ui.Button(
                style=discord.ButtonStyle.secondary,
                label="🔐 إدارة الصلاحيات",
                custom_id="wos:settings:permissions",
                row=0
            ))
        self.add_item(ui.Button(
            style=discord.ButtonStyle.gray,
            label="⬅️ رجوع",
            custom_id="wos:main:back",
            row=3
        ))
