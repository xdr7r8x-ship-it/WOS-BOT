import discord


COLOR_SUCCESS = 0x00FF00
COLOR_WARNING = 0xF39C12
COLOR_ERROR = 0xE74C3C
COLOR_INFO = 0x3498DB
COLOR_NEUTRAL = 0x95A5A6


def create_main_embed() -> discord.Embed:
    embed = discord.Embed(
        title="WOS Control Panel",
        description="لوحة التحكم الرئيسية لبوت WOS",
        color=COLOR_INFO
    )
    embed.set_footer(text="استخدم الأزرار للتنقل")
    return embed


def create_success_embed(title: str, description: str) -> discord.Embed:
    return discord.Embed(
        title=title,
        description=description,
        color=COLOR_SUCCESS
    )


def create_error_embed(title: str, description: str) -> discord.Embed:
    return discord.Embed(
        title=title,
        description=description,
        color=COLOR_ERROR
    )


def create_warning_embed(title: str, description: str) -> discord.Embed:
    return discord.Embed(
        title=title,
        description=description,
        color=COLOR_WARNING
    )


def create_info_embed(title: str, description: str) -> discord.Embed:
    return discord.Embed(
        title=title,
        description=description,
        color=COLOR_INFO
    )


def create_field_embed(title: str, fields: list) -> discord.Embed:
    embed = discord.Embed(title=title, color=COLOR_NEUTRAL)
    for name, value, inline in fields:
        embed.add_field(name=name, value=value, inline=inline)
    return embed


def create_section_embed(title: str, description: str = "") -> discord.Embed:
    return discord.Embed(
        title=title,
        description=description,
        color=COLOR_INFO
    )


def create_timeout_embed() -> discord.Embed:
    return discord.Embed(
        title="⏰ انتهت صلاحية لوحة التحكم",
        description="استخدم /wos من جديد",
        color=COLOR_WARNING
    )


def create_unauthorized_embed() -> discord.Embed:
    return discord.Embed(
        title="⛔ غير مصرح",
        description="غير مصرح لك بتنفيذ هذا الإجراء",
        color=COLOR_ERROR
    )


def sanitize_embed_value(value: str, max_length: int = 1024) -> str:
    if not value:
        return ""
    value = str(value)
    if len(value) > max_length:
        value = value[:max_length - 3] + "..."
    return value
