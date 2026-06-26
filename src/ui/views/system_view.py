import discord
from discord import ui

from src.ui.components.embeds import create_section_embed, create_unauthorized_embed
from src.ui.components.guards import check_admin_permission, log_panel_action


class SystemView(ui.View):
    def __init__(self):
        super().__init__(timeout=300)
        self.add_buttons()

    def add_buttons(self):
        self.add_item(ui.Button(
            style=discord.ButtonStyle.danger,
            label="📊 System",
            custom_id="wos:system:info",
            row=0
        ))
        self.add_item(ui.Button(
            style=discord.ButtonStyle.danger,
            label="🧪 Diagnostics",
            custom_id="wos:system:diagnostics",
            row=0
        ))
        self.add_item(ui.Button(
            style=discord.ButtonStyle.danger,
            label="🧬 Integrity",
            custom_id="wos:system:integrity",
            row=1
        ))
        self.add_item(ui.Button(
            style=discord.ButtonStyle.secondary,
            label="🧠 Autopilot",
            custom_id="wos:system:autopilot",
            row=1
        ))
        self.add_item(ui.Button(
            style=discord.ButtonStyle.secondary,
            label="👁️ Watchdog",
            custom_id="wos:system:watchdog",
            row=2
        ))
        self.add_item(ui.Button(
            style=discord.ButtonStyle.secondary,
            label="🔮 Predict",
            custom_id="wos:system:predict",
            row=2
        ))
        self.add_item(ui.Button(
            style=discord.ButtonStyle.gray,
            label="⬅️ رجوع",
            custom_id="wos:system:back",
            row=3
        ))
