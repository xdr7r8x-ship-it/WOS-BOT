import discord
from discord import ui

from src.services.admin_access_service import check_permission
from src.services.alliance_service import get_active_alliances, get_alliance_member_count
from src.services.alliance_member_service import get_alliance_members
from src.ui.components.embeds import create_section_embed, create_success_embed, create_error_embed


class AllianceView(ui.View):
    def __init__(self, user_id: str, guild_id: str):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.guild_id = guild_id
        self.add_buttons()

    def add_buttons(self):
        if check_permission(self.guild_id, self.user_id, "ALLIANCE_VIEW"):
            self.add_item(ui.Button(
                style=discord.ButtonStyle.primary,
                label="📋 قائمة التحالفات",
                custom_id="wos:alliance:list",
                row=0
            ))
        
        if check_permission(self.guild_id, self.user_id, "ALLIANCE_CREATE"):
            self.add_item(ui.Button(
                style=discord.ButtonStyle.success,
                label="➕ إضافة تحالف",
                custom_id="wos:alliance:create",
                row=0
            ))
        
        if check_permission(self.guild_id, self.user_id, "ALLIANCE_UPDATE"):
            self.add_item(ui.Button(
                style=discord.ButtonStyle.secondary,
                label="✏️ تعديل تحالف",
                custom_id="wos:alliance:edit",
                row=1
            ))
        
        if check_permission(self.guild_id, self.user_id, "ALLIANCE_DISABLE"):
            self.add_item(ui.Button(
                style=discord.ButtonStyle.danger,
                label="⛔ تعطيل تحالف",
                custom_id="wos:alliance:disable",
                row=1
            ))
        
        if check_permission(self.guild_id, self.user_id, "ALLIANCE_MEMBERS_VIEW"):
            self.add_item(ui.Button(
                style=discord.ButtonStyle.primary,
                label="👥 أعضاء التحالف",
                custom_id="wos:alliance:members",
                row=2
            ))
        
        if check_permission(self.guild_id, self.user_id, "ALLIANCE_MEMBER_RANK_UPDATE"):
            self.add_item(ui.Button(
                style=discord.ButtonStyle.secondary,
                label="⭐ إدارة الرتب",
                custom_id="wos:alliance:ranks",
                row=2
            ))
        
        if check_permission(self.guild_id, self.user_id, "ALLIANCE_STATS_VIEW"):
            self.add_item(ui.Button(
                style=discord.ButtonStyle.primary,
                label="📊 إحصائيات",
                custom_id="wos:alliance:stats",
                row=3
            ))
        
        if check_permission(self.guild_id, self.user_id, "ALLIANCE_API_SYNC"):
            self.add_item(ui.Button(
                style=discord.ButtonStyle.success,
                label="🔄 مزامنة API",
                custom_id="wos:alliance:sync",
                row=3
            ))
        
        if check_permission(self.guild_id, self.user_id, "ALLIANCE_API_HEALTH"):
            self.add_item(ui.Button(
                style=discord.ButtonStyle.secondary,
                label="🧪 حالة API",
                custom_id="wos:alliance:api_health",
                row=3
            ))
        
        if check_permission(self.guild_id, self.user_id, "ALLIANCE_AUDIT_VIEW"):
            self.add_item(ui.Button(
                style=discord.ButtonStyle.gray,
                label="📜 سجل التحالفات",
                custom_id="wos:alliance:audit",
                row=4
            ))
        
        self.add_item(ui.Button(
            style=discord.ButtonStyle.gray,
            label="⬅️ رجوع",
            custom_id="wos:main:back",
            row=4
        ))


class AllianceListView(ui.View):
    def __init__(self, user_id: str, guild_id: str):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.guild_id = guild_id
        self.build_list()

    def build_list(self):
        alliances = get_active_alliances(self.guild_id)
        for alliance in alliances[:10]:
            member_count = get_alliance_member_count(alliance["id"])
            self.add_item(ui.Button(
                style=discord.ButtonStyle.secondary,
                label=f"🏰 {alliance['alliance_tag']} ({member_count})",
                custom_id=f"wos:alliance:view:{alliance['id']}",
                row=0
            ))
