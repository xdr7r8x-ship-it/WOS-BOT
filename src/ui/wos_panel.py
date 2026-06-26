import discord
from discord import app_commands

from src.ui.components.embeds import (
    create_main_embed, create_section_embed, create_field_embed,
    create_success_embed, create_error_embed, create_timeout_embed,
    create_unauthorized_embed, sanitize_embed_value, COLOR_SUCCESS,
    COLOR_WARNING, COLOR_ERROR, COLOR_INFO
)
from src.ui.components.guards import (
    check_admin_permission, log_panel_action
)
from src.ui.views.main_view import MainView
from src.ui.views.redeem_view import RedeemView, RedeemCodeModal, StatusCodeModal
from src.ui.views.player_view import PlayerView, PlayerRemoveModal
from src.ui.views.security_view import SecurityView
from src.ui.views.system_view import SystemView
from src.ui.views.backup_view import BackupView, RollbackConfirmView
from src.ui.views.update_view import UpdateView, UpdateConfirmView
from src.ui.views.maintenance_view import MaintenanceView
from src.ui.views.settings_view import SettingsView
from src.ui.views.language_view import LanguageView
from src.services.admin_access_service import (
    is_authorized, is_owner, authorize_and_log, record_access_denial,
    check_permission, get_role_level
)
from src.services.language_service import get_user_language, set_user_language
from src.i18n import t
from src.ui.components.view_state import ViewState


SAFE_ALLOWED_MENTIONS = discord.AllowedMentions.none()


async def handle_wos_command(interaction: discord.Interaction):
    guild_id = str(interaction.guild_id) if interaction.guild else "0"
    user_id = str(interaction.user.id) if interaction.user else "0"
    
    if not is_authorized(guild_id, user_id):
        record_access_denial(guild_id, user_id, "WOS_OPEN", "Not authorized")
        await interaction.response.send_message(
            embed=create_unauthorized_embed(),
            ephemeral=True,
            allowed_mentions=SAFE_ALLOWED_MENTIONS
        )
        return
    
    authorize_and_log(guild_id, user_id, "WOS_OPEN")
    lang = get_user_language(guild_id, user_id)
    await interaction.response.send_message(
        embed=create_main_embed(),
        view=MainView(user_id, guild_id),
        ephemeral=True,
        allowed_mentions=SAFE_ALLOWED_MENTIONS
    )


async def handle_button(interaction: discord.Interaction):
    custom_id = interaction.data.get("custom_id", "")
    guild_id = str(interaction.guild_id) if interaction.guild else "0"
    user_id = str(interaction.user.id) if interaction.user else "0"
    lang = get_user_language(guild_id, user_id)
    
    if custom_id.startswith("wos:language:"):
        await handle_language_button(interaction, custom_id, guild_id, user_id, lang)
        return
    
    if custom_id.startswith("wos:content:"):
        await handle_content_button(interaction, custom_id, guild_id, user_id, lang)
        return
    
    if custom_id.startswith("wos:reminder:"):
        if custom_id == "wos:reminder:open":
            await handle_reminder_section(interaction, "")
        else:
            await handle_reminder_button(interaction, custom_id, guild_id, user_id, lang)
        return
    
    if custom_id.startswith("wos:player_id:"):
        if custom_id == "wos:player_id:open":
            await handle_player_id_section(interaction, "")
        else:
            await handle_player_id_button(interaction, custom_id, guild_id, user_id, lang)
        return
    
    if not is_authorized(guild_id, user_id):
        record_access_denial(guild_id, user_id, f"BUTTON:{custom_id}", "Not authorized")
        await interaction.response.send_message(
            embed=create_unauthorized_embed(),
            ephemeral=True,
            allowed_mentions=SAFE_ALLOWED_MENTIONS
        )
        return
    
    parts = custom_id.split(":")
    if len(parts) < 2:
        return
    
    section = parts[1]
    action = parts[2] if len(parts) > 2 else ""
    
    handlers = {
        "main": handle_main_section,
        "redeem": handle_redeem_section,
        "players": handle_players_section,
        "security": handle_security_section,
        "system": handle_system_section,
        "backup": handle_backup_section,
        "update": handle_update_section,
        "maintenance": handle_maintenance_section,
        "settings": handle_settings_section,
        "alliance": handle_alliance_section,
    }
    
    handler = handlers.get(section)
    if handler:
        try:
            await interaction.defer()
        except:
            pass
        await handler(interaction, action)
    else:
        await interaction.followup.send(
            embed=create_error_embed(t("errors.generic", lang), ""),
            ephemeral=True,
            allowed_mentions=SAFE_ALLOWED_MENTIONS
        )


async def handle_language_button(interaction: discord.Interaction, custom_id: str, guild_id: str, user_id: str, lang: str):
    action = custom_id.split(":")[-1]
    
    if action == "open":
        await interaction.response.send_message(
            embed=create_section_embed(t("language.title", lang)),
            view=LanguageView(user_id, guild_id, lang),
            ephemeral=True,
            allowed_mentions=SAFE_ALLOWED_MENTIONS
        )
        return
    
    if action in ["ar", "en"]:
        old_lang = lang
        new_lang = action
        set_user_language(guild_id, user_id, new_lang)
        save_audit_log(guild_id, user_id, "LANGUAGE_CHANGED", "", "SUCCESS", "LOW", f"{{\"old_language\": \"{old_lang}\", \"new_language\": \"{new_lang}\"}}")
        confirmation = t(f"language.changed_to_{new_lang}", new_lang)
        await interaction.response.send_message(
            embed=create_success_embed(t("common.success", new_lang), confirmation),
            ephemeral=True,
            allowed_mentions=SAFE_ALLOWED_MENTIONS
        )
        return
    
    if action == "cancel":
        await interaction.response.send_message(
            embed=create_success_embed(t("common.success", lang), t("common.cancel", lang)),
            ephemeral=True,
            allowed_mentions=SAFE_ALLOWED_MENTIONS
        )
        return


async def handle_content_button(interaction: discord.Interaction, custom_id: str, guild_id: str, user_id: str, lang: str):
    from src.services.admin_access_service import check_permission
    from src.ui.views.content_block_select_view import ContentBlockSelectView
    
    action = custom_id.split(":")[-1]
    parts = custom_id.split(":")
    
    if not check_permission(guild_id, user_id, "CONTENT_EDIT"):
        save_audit_log(guild_id, user_id, "PAGE_CONTENT_PERMISSION_DENIED", action, "DENIED", "LOW")
        await interaction.response.send_message(
            embed=create_error_embed(t("common.no_permission", lang), t("content.no_permission", lang)),
            ephemeral=True,
            allowed_mentions=SAFE_ALLOWED_MENTIONS
        )
        return
    
    if len(parts) >= 3 and parts[2] in ["open", "history"]:
        page_key = parts[3] if len(parts) > 3 else "main_panel"
        
        if parts[2] == "history":
            from src.services.content_audit_service import get_content_history
            history = get_content_history(guild_id, page_key=page_key, limit=20)
            
            desc = t("content.history_empty", lang)
            if history:
                desc = "\n".join([f"• {h['block_key']}: {h['action']} ({h['created_at'][:10]})" for h in history[:10]])
            
            await interaction.response.send_message(
                embed=discord.Embed(
                    title=t("content.history_title", lang),
                    description=desc,
                    color=discord.Color.blue()
                ),
                ephemeral=True,
                allowed_mentions=SAFE_ALLOWED_MENTIONS
            )
            return
        
        await interaction.response.send_message(
            embed=create_section_embed(t("content.title", lang), t("content.description", lang)),
            view=ContentBlockSelectView(user_id, guild_id, page_key, lang),
            ephemeral=True,
            allowed_mentions=SAFE_ALLOWED_MENTIONS
        )
        return
    
    if action == "cancel":
        await interaction.response.send_message(
            embed=create_success_embed(t("common.success", lang), t("common.close", lang)),
            ephemeral=True,
            allowed_mentions=SAFE_ALLOWED_MENTIONS
        )
        return


def save_audit_log(guild_id: str, actor_id: str, action: str, target: str, result: str, risk_level: str, metadata: str = None):
    from database import save_audit_log as db_save_audit_log
    try:
        db_save_audit_log(guild_id, actor_id, action, target, result, risk_level, metadata)
    except Exception:
        pass


async def handle_main_section(interaction: discord.Interaction, action: str):
    views = {
        "redeem": RedeemView,
        "players": PlayerView,
        "security": SecurityView,
        "system": SystemView,
        "backup": BackupView,
        "update": UpdateView,
        "maintenance": MaintenanceView,
    }
    
    view_class = views.get(action)
    if view_class:
        await interaction.followup.send(
            embed=create_section_embed(f"WOS - {get_section_title(action)}"),
            view=view_class(),
            ephemeral=True,
            allowed_mentions=SAFE_ALLOWED_MENTIONS
        )
    elif action == "health":
        await show_health(interaction)
    else:
        await interaction.followup.send(
            embed=create_main_embed(),
            view=MainView(),
            ephemeral=True,
            allowed_mentions=SAFE_ALLOWED_MENTIONS
        )


async def handle_redeem_section(interaction: discord.Interaction, action: str):
    if action == "add":
        await interaction.followup.send(
            view=RedeemCodeModal(),
            ephemeral=True,
            allowed_mentions=SAFE_ALLOWED_MENTIONS
        )
    elif action == "status":
        await interaction.followup.send(
            view=StatusCodeModal(),
            ephemeral=True,
            allowed_mentions=SAFE_ALLOWED_MENTIONS
        )
    elif action == "queue":
        await show_queue_status(interaction)
    elif action == "back":
        await interaction.followup.send(
            embed=create_main_embed(),
            view=MainView(),
            ephemeral=True,
            allowed_mentions=SAFE_ALLOWED_MENTIONS
        )


async def handle_players_section(interaction: discord.Interaction, action: str):
    if action == "list":
        await show_player_list(interaction)
    elif action == "remove":
        await interaction.followup.send(
            view=PlayerRemoveModal(),
            ephemeral=True,
            allowed_mentions=SAFE_ALLOWED_MENTIONS
        )
    elif action == "count":
        await show_player_count(interaction)
    elif action == "back":
        await interaction.followup.send(
            embed=create_main_embed(),
            view=MainView(),
            ephemeral=True,
            allowed_mentions=SAFE_ALLOWED_MENTIONS
        )


async def handle_security_section(interaction: discord.Interaction, action: str):
    allowed, reason = await check_admin_permission(interaction, "security_scan")
    if not allowed:
        await interaction.followup.send(
            embed=create_unauthorized_embed(),
            ephemeral=True,
            allowed_mentions=SAFE_ALLOWED_MENTIONS
        )
        return
    
    handlers = {
        "scan": show_security_scan,
        "audit": show_audit_logs,
        "blocked": show_blocked_users,
        "incidents": show_security_incidents,
    }
    
    handler = handlers.get(action)
    if handler:
        await handler(interaction)
    elif action == "back":
        await interaction.followup.send(
            embed=create_main_embed(),
            view=MainView(),
            ephemeral=True,
            allowed_mentions=SAFE_ALLOWED_MENTIONS
        )


async def handle_system_section(interaction: discord.Interaction, action: str):
    handlers = {
        "info": show_system_info,
        "diagnostics": show_diagnostics,
        "integrity": show_integrity,
        "autopilot": show_autopilot,
        "watchdog": show_watchdog,
        "predict": show_predict,
    }
    
    handler = handlers.get(action)
    if handler:
        await handler(interaction)
    elif action == "back":
        await interaction.followup.send(
            embed=create_main_embed(),
            view=MainView(),
            ephemeral=True,
            allowed_mentions=SAFE_ALLOWED_MENTIONS
        )


async def handle_backup_section(interaction: discord.Interaction, action: str):
    handlers = {
        "create": create_backup,
        "list": list_backups,
        "rollback_confirm": confirm_rollback,
        "rollback_execute": execute_rollback,
        "rollback_cancel": cancel_rollback,
    }
    
    handler = handlers.get(action)
    if handler:
        await handler(interaction)
    elif action == "back":
        await interaction.followup.send(
            embed=create_main_embed(),
            view=MainView(),
            ephemeral=True,
            allowed_mentions=SAFE_ALLOWED_MENTIONS
        )


async def handle_update_section(interaction: discord.Interaction, action: str):
    handlers = {
        "check": check_updates,
        "plan": show_update_plan,
        "apply_confirm": confirm_update,
        "apply_execute": execute_update,
        "apply_cancel": cancel_update,
    }
    
    handler = handlers.get(action)
    if handler:
        await handler(interaction)
    elif action == "back":
        await interaction.followup.send(
            embed=create_main_embed(),
            view=MainView(),
            ephemeral=True,
            allowed_mentions=SAFE_ALLOWED_MENTIONS
        )


async def handle_maintenance_section(interaction: discord.Interaction, action: str):
    handlers = {
        "cleanup": run_cleanup,
        "retry": run_retry,
        "logs": show_logs_status,
    }
    
    handler = handlers.get(action)
    if handler:
        await handler(interaction)
    elif action == "back":
        await interaction.followup.send(
            embed=create_main_embed(),
            view=MainView(),
            ephemeral=True,
            allowed_mentions=SAFE_ALLOWED_MENTIONS
        )


async def show_health(interaction: discord.Interaction):
    from src.services.health_service import health_service
    guild_id = str(interaction.guild_id) if interaction.guild else "0"
    health = health_service.get_health(guild_id)
    
    fields = [
        ("الحالة", "🟢 Online" if health["status"] == "online" else "🔴 Offline", True),
        ("Queue", str(health["queue_size"]), True),
        ("Retry Jobs", str(health["retry_jobs"]), True),
        ("Players", str(health["active_players"]), True),
        ("API", "🟡 Paused" if health["api_status"] == "paused" else "🟢 OK", True),
        ("DB", health["db_size"], True),
        ("Success", str(health["total_success"]), True),
        ("Failed", str(health["total_failed"]), True),
    ]
    
    await interaction.followup.send(
        embed=create_field_embed("📊 حالة البوت", fields),
        ephemeral=True,
        allowed_mentions=SAFE_ALLOWED_MENTIONS
    )


async def show_queue_status(interaction: discord.Interaction):
    from database import get_queue_count, get_retry_job_count, get_processed_codes_stats
    guild_id = str(interaction.guild_id) if interaction.guild else "0"
    
    queue_count = get_queue_count()
    retry_count = get_retry_job_count()
    stats = get_processed_codes_stats(guild_id)
    
    fields = [
        ("الأكواد في Queue", str(queue_count), True),
        ("Retry Jobs", str(retry_count), True),
        ("تمت معالجتها", str(stats.get("processed", 0)), True),
        ("فشلت", str(stats.get("failed", 0)), True),
    ]
    
    await interaction.followup.send(
        embed=create_field_embed("📋 حالة Queue", fields),
        ephemeral=True,
        allowed_mentions=SAFE_ALLOWED_MENTIONS
    )


async def show_player_list(interaction: discord.Interaction):
    from database import get_active_players
    guild_id = str(interaction.guild_id) if interaction.guild else "0"
    players = get_active_players(guild_id)
    
    if not players:
        embed = create_field_embed("👥 قائمة اللاعبين", [("النتيجة", "لا يوجد لاعبون مسجلون", True)])
    else:
        player_list = "\n".join(players[:50])
        if len(players) > 50:
            player_list += f"\n... و {len(players) - 50} المزيد"
        embed = create_field_embed(f"👥 اللاعبون ({len(players)})", [("Player IDs", sanitize_embed_value(player_list), False)])
    
    await interaction.followup.send(
        embed=embed,
        ephemeral=True,
        allowed_mentions=SAFE_ALLOWED_MENTIONS
    )


async def show_player_count(interaction: discord.Interaction):
    from database import get_player_count
    guild_id = str(interaction.guild_id) if interaction.guild else "0"
    count = get_player_count(guild_id)
    
    fields = [
        ("إجمالي اللاعبين", str(count.get("total", 0)), True),
        ("النشطون", str(count.get("active", 0)), True),
        ("المعطلون", str(count.get("disabled", 0)), True),
    ]
    
    await interaction.followup.send(
        embed=create_field_embed("📊 عدد اللاعبين", fields),
        ephemeral=True,
        allowed_mentions=SAFE_ALLOWED_MENTIONS
    )


async def show_security_scan(interaction: discord.Interaction):
    from src.services.security_service import security_service
    results = security_service.run_security_scan()
    color = {"PASS": COLOR_SUCCESS, "WARN": COLOR_WARNING, "FAIL": COLOR_ERROR}.get(results["overall_status"], COLOR_INFO)
    
    fields = [("النتيجة", results["overall_status"], True)]
    for name, check in results.get("checks", {}).items():
        status = check.get("status", "UNKNOWN")
        fields.append((name.replace("_", " ").title(), status, True))
    
    embed = discord.Embed(title="🔒 فحص الحماية", color=color)
    for name, value, inline in fields:
        embed.add_field(name=name, value=value, inline=inline)
    
    await interaction.followup.send(
        embed=embed,
        ephemeral=True,
        allowed_mentions=SAFE_ALLOWED_MENTIONS
    )


async def show_audit_logs(interaction: discord.Interaction):
    from database import get_recent_audit_logs
    guild_id = str(interaction.guild_id) if interaction.guild else "0"
    logs = get_recent_audit_logs(guild_id, limit=10)
    
    if not logs:
        embed = create_field_embed("📜 Audit Logs", [("النتيجة", "لا توجد سجلات", True)])
    else:
        fields = []
        for log in logs[:10]:
            action = sanitize_embed_value(log.get("action", "UNKNOWN"), 30)
            result = log.get("result", "")
            fields.append((action, result, True))
        embed = create_field_embed("📜 Audit Logs (الأخيرة)", fields)
    
    await interaction.followup.send(
        embed=embed,
        ephemeral=True,
        allowed_mentions=SAFE_ALLOWED_MENTIONS
    )


async def show_blocked_users(interaction: discord.Interaction):
    from database import get_blocked_users
    guild_id = str(interaction.guild_id) if interaction.guild else "0"
    blocked = get_blocked_users(guild_id)
    
    if not blocked:
        embed = create_field_embed("🚫 المحظورون", [("النتيجة", "لا يوجد محظورون", True)])
    else:
        fields = [(sanitize_embed_value(str(b.get("user_id", "")), 15), b.get("reason", ""), True) for b in blocked[:10]]
        embed = create_field_embed(f"🚫 المحظورون ({len(blocked)})", fields)
    
    await interaction.followup.send(
        embed=embed,
        ephemeral=True,
        allowed_mentions=SAFE_ALLOWED_MENTIONS
    )


async def show_security_incidents(interaction: discord.Interaction):
    from database import get_recent_security_incidents
    guild_id = str(interaction.guild_id) if interaction.guild else "0"
    incidents = get_recent_security_incidents(guild_id, limit=10)
    
    if not incidents:
        embed = create_field_embed("⚠️ الحوادث الأمنية", [("النتيجة", "لا توجد حوادث", True)])
    else:
        fields = []
        for inc in incidents[:10]:
            incident_type = sanitize_embed_value(inc.get("incident_type", "UNKNOWN"), 20)
            severity = inc.get("severity", "")
            fields.append((incident_type, severity, True))
        embed = create_field_embed("⚠️ الحوادث الأمنية (الأخيرة)", fields)
    
    await interaction.followup.send(
        embed=embed,
        ephemeral=True,
        allowed_mentions=SAFE_ALLOWED_MENTIONS
    )


async def show_system_info(interaction: discord.Interaction):
    from src.services.version_service import read_version
    from src.utils.system import get_memory_info, get_disk_info, get_uptime
    from src.utils.time import format_uptime
    from src.services.backup_service import backup_service
    from src.services.autopilot_service import autopilot_service
    from database import get_db_size, get_retry_job_count, get_queue_count
    
    version = read_version()
    mem = get_memory_info()
    disk = get_disk_info("/")
    uptime = get_uptime()
    autopilot_status = autopilot_service.get_status()
    latest_backup = backup_service.get_latest()
    
    fields = [
        ("Bot Version", version or "Unknown", True),
        ("Uptime", format_uptime(uptime), True),
        ("Memory", f"{mem['percent']:.1f}%", True),
        ("Disk", f"{disk['percent']:.1f}%", True),
        ("Queue", str(get_queue_count()), True),
        ("Retry Jobs", str(get_retry_job_count()), True),
        ("DB Size", get_db_size(), True),
        ("Last Backup", latest_backup['created_at'][:10] if latest_backup else "None", True),
        ("Autopilot", autopilot_status.get("overall_status", "Unknown"), True),
    ]
    
    await interaction.followup.send(
        embed=create_field_embed("⚙️ System Information", fields),
        ephemeral=True,
        allowed_mentions=SAFE_ALLOWED_MENTIONS
    )


async def show_diagnostics(interaction: discord.Interaction):
    from src.services.diagnostics_service import diagnostics_service
    
    results = await diagnostics_service.run_full_diagnostics()
    color = {"PASS": COLOR_SUCCESS, "WARN": COLOR_WARNING, "FAIL": COLOR_ERROR}.get(results["overall_status"], COLOR_INFO)
    
    fields = [("Overall", results["overall_status"], True)]
    for name, check in results.get("checks", {}).items():
        status = check.get("status", "UNKNOWN")
        fields.append((name.replace("_", " ").title(), status, True))
    
    embed = discord.Embed(title="🧪 Diagnostics", color=color)
    for name, value, inline in fields:
        embed.add_field(name=name, value=value, inline=inline)
    
    await interaction.followup.send(
        embed=embed,
        ephemeral=True,
        allowed_mentions=SAFE_ALLOWED_MENTIONS
    )


async def show_integrity(interaction: discord.Interaction):
    from src.services.integrity_service import integrity_service
    
    results = integrity_service.run_integrity_check()
    color = {"PASS": COLOR_SUCCESS, "WARN": COLOR_WARNING, "FAIL": COLOR_ERROR}.get(results["overall_status"], COLOR_INFO)
    
    fields = [("Result", results["overall_status"], True)]
    for name, check in results.get("checks", {}).items():
        status = check.get("status", "UNKNOWN")
        fields.append((name.replace("_", " ").title(), status, True))
    
    embed = discord.Embed(title="🧬 Integrity Check", color=color)
    for name, value, inline in fields:
        embed.add_field(name=name, value=value, inline=inline)
    
    await interaction.followup.send(
        embed=embed,
        ephemeral=True,
        allowed_mentions=SAFE_ALLOWED_MENTIONS
    )


async def show_autopilot(interaction: discord.Interaction):
    from src.services.autopilot_service import autopilot_service
    
    status = autopilot_service.get_status()
    fields = [("Overall", status.get("overall_status", "Unknown"), True)]
    
    services = status.get("services", {})
    for name, svc in services.items():
        status_icon = "🟢" if svc.get("status") == "RUNNING" else "🔴"
        fields.append((f"{status_icon} {name}", f"Failures: {svc.get('consecutive_failures', 0)}", True))
    
    await interaction.followup.send(
        embed=create_field_embed("🧠 Autopilot Status", fields),
        ephemeral=True,
        allowed_mentions=SAFE_ALLOWED_MENTIONS
    )


async def show_watchdog(interaction: discord.Interaction):
    from src.services.watchdog_service import watchdog_service
    
    status = watchdog_service.get_status()
    services = status.get("services", [])
    
    if not services:
        embed = create_field_embed("👁️ Watchdog Status", [("النتيجة", "No services monitored", True)])
    else:
        fields = []
        for svc in services:
            name = sanitize_embed_value(svc.get("service_name", "unknown"), 20)
            stat = svc.get("status", "UNKNOWN")
            failures = svc.get("consecutive_failures", 0)
            fields.append((name, f"{stat} ({failures} failures)", True))
        embed = create_field_embed("👁️ Watchdog Status", fields)
    
    await interaction.followup.send(
        embed=embed,
        ephemeral=True,
        allowed_mentions=SAFE_ALLOWED_MENTIONS
    )


async def show_predict(interaction: discord.Interaction):
    from src.services.predictive_service import predictive_service
    
    events = predictive_service.get_active_predictions()
    
    if not events:
        embed = create_field_embed("🔮 Predictions", [("النتيجة", "No active warnings", True)])
    else:
        fields = []
        for event in events[:10]:
            ptype = sanitize_embed_value(event.get("prediction_type", "Unknown"), 20)
            severity = event.get("severity", "")
            fields.append((ptype, f"[{severity}]", True))
        embed = create_field_embed("🔮 Predictions", fields)
    
    await interaction.followup.send(
        embed=embed,
        ephemeral=True,
        allowed_mentions=SAFE_ALLOWED_MENTIONS
    )


async def create_backup(interaction: discord.Interaction):
    from src.services.backup_service import backup_service
    from src.services.alert_service import alert_service
    from src.ui.components.guards import log_panel_action
    
    guild_id = str(interaction.guild_id) if interaction.guild else "0"
    user_id = str(interaction.user.id) if interaction.user else "0"
    
    allowed, reason = await check_admin_permission(interaction, "backup_create")
    if not allowed:
        await interaction.followup.send(
            embed=create_unauthorized_embed(),
            ephemeral=True,
            allowed_mentions=SAFE_ALLOWED_MENTIONS
        )
        return
    
    success, path = backup_service.create_backup()
    
    if success:
        log_panel_action(guild_id, user_id, "BACKUP_CREATED", path, "SUCCESS", "MEDIUM")
        await alert_service.send_backup_alert(True, path)
        await interaction.followup.send(
            embed=create_success_embed("✅ تم", "تم إنشاء Backup بنجاح"),
            ephemeral=True,
            allowed_mentions=SAFE_ALLOWED_MENTIONS
        )
    else:
        await interaction.followup.send(
            embed=create_error_embed("❌ خطأ", "فشل في إنشاء Backup"),
            ephemeral=True,
            allowed_mentions=SAFE_ALLOWED_MENTIONS
        )


async def list_backups(interaction: discord.Interaction):
    from src.services.backup_service import backup_service
    
    backups = backup_service.list_backups()
    
    if not backups:
        embed = create_field_embed("📦 Backups", [("النتيجة", "No backups found", True)])
    else:
        fields = []
        for i, backup in enumerate(backups[:10]):
            name = sanitize_embed_value(backup.get("backup_name", ""), 30)
            size = f"{backup.get('size_bytes', 0) / 1024:.1f} KB"
            date = backup.get('created_at', '')[:10]
            fields.append((f"{i+1}. {name}", f"Size: {size}\nDate: {date}", False))
        embed = create_field_embed("📦 Backups", fields)
    
    await interaction.followup.send(
        embed=embed,
        ephemeral=True,
        allowed_mentions=SAFE_ALLOWED_MENTIONS
    )


async def confirm_rollback(interaction: discord.Interaction):
    from src.services.rollback_service import rollback_service
    
    allowed, reason = await check_admin_permission(interaction, "rollback")
    if not allowed:
        await interaction.followup.send(
            embed=create_unauthorized_embed(),
            ephemeral=True,
            allowed_mentions=SAFE_ALLOWED_MENTIONS
        )
        return
    
    if not rollback_service.can_rollback():
        await interaction.followup.send(
            embed=create_error_embed("❌ خطأ", "لا يوجد Backup متاح"),
            ephemeral=True,
            allowed_mentions=SAFE_ALLOWED_MENTIONS
        )
        return
    
    await interaction.followup.send(
        embed=create_warning_embed("⚠️ تأكيد Rollback", "هل أنت متأكد؟ هذا الإجراء لا يمكن التراجع عنه."),
        view=RollbackConfirmView(),
        ephemeral=True,
        allowed_mentions=SAFE_ALLOWED_MENTIONS
    )


async def execute_rollback(interaction: discord.Interaction):
    from src.services.rollback_service import rollback_service
    from src.services.alert_service import alert_service
    from src.ui.components.guards import log_panel_action
    
    guild_id = str(interaction.guild_id) if interaction.guild else "0"
    user_id = str(interaction.user.id) if interaction.user else "0"
    
    success, msg = rollback_service.restore_latest_backup()
    
    if success:
        log_panel_action(guild_id, user_id, "ROLLBACK_CONFIRMED", "rollback", "SUCCESS", "HIGH")
        await alert_service.send_alert("Rollback", msg, "INFO")
        await interaction.followup.send(
            embed=create_success_embed("✅ تم", msg),
            ephemeral=True,
            allowed_mentions=SAFE_ALLOWED_MENTIONS
        )
    else:
        await interaction.followup.send(
            embed=create_error_embed("❌ خطأ", "فشل في Rollback"),
            ephemeral=True,
            allowed_mentions=SAFE_ALLOWED_MENTIONS
        )


async def cancel_rollback(interaction: discord.Interaction):
    await interaction.followup.send(
        embed=create_info_embed("ℹ️ تم الإلغاء", "تم إلغاء Rollback"),
        ephemeral=True,
        allowed_mentions=SAFE_ALLOWED_MENTIONS
    )


async def check_updates(interaction: discord.Interaction):
    from src.services.update_service import update_service
    
    allowed, reason = await check_admin_permission(interaction, "updates_check")
    if not allowed:
        await interaction.followup.send(
            embed=create_unauthorized_embed(),
            ephemeral=True,
            allowed_mentions=SAFE_ALLOWED_MENTIONS
        )
        return
    
    has_update, version = await update_service.check_for_updates()
    
    if has_update:
        await interaction.followup.send(
            embed=create_info_embed("📦 تحديث متاح", f"الإصدار: {version}"),
            ephemeral=True,
            allowed_mentions=SAFE_ALLOWED_MENTIONS
        )
    else:
        await interaction.followup.send(
            embed=create_success_embed("✅ محدث", "البوت محدث"),
            ephemeral=True,
            allowed_mentions=SAFE_ALLOWED_MENTIONS
        )


async def show_update_plan(interaction: discord.Interaction):
    from src.services.update_service import update_service
    
    plan = update_service.create_update_plan()
    
    fields = [
        ("Can Update", str(plan.get("can_update", False)), True),
        ("Current", plan.get("current_version", "Unknown"), True),
        ("Latest", plan.get("latest_version", "Unknown"), True),
        ("Type", plan.get("update_type", "Unknown"), True),
    ]
    if plan.get("reason"):
        fields.append(("Reason", plan["reason"], False))
    
    await interaction.followup.send(
        embed=create_field_embed("📋 خطة التحديث", fields),
        ephemeral=True,
        allowed_mentions=SAFE_ALLOWED_MENTIONS
    )


async def confirm_update(interaction: discord.Interaction):
    await interaction.followup.send(
        embed=create_warning_embed("⚠️ تأكيد التحديث", "هل أنت متأكد؟ سيتم تطبيق التحديث."),
        view=UpdateConfirmView(),
        ephemeral=True,
        allowed_mentions=SAFE_ALLOWED_MENTIONS
    )


async def execute_update(interaction: discord.Interaction):
    from src.services.update_service import update_service
    from src.services.diagnostics_service import diagnostics_service
    from src.services.security_service import security_service
    from src.services.integrity_service import integrity_service
    from src.services.alert_service import alert_service
    from src.ui.components.guards import log_panel_action
    
    guild_id = str(interaction.guild_id) if interaction.guild else "0"
    user_id = str(interaction.user.id) if interaction.user else "0"
    
    diagnostics = await diagnostics_service.run_full_diagnostics()
    if diagnostics["overall_status"] == "FAIL":
        log_panel_action(guild_id, user_id, "UPDATE_BLOCKED", "updates_apply", "BLOCKED", "CRITICAL", "Diagnostics failed")
        await interaction.followup.send(
            embed=create_error_embed("❌ مرفوض", "يجب نجاح Diagnostics قبل التحديث"),
            ephemeral=True,
            allowed_mentions=SAFE_ALLOWED_MENTIONS
        )
        return
    
    security = security_service.run_security_scan()
    if security["overall_status"] == "FAIL":
        log_panel_action(guild_id, user_id, "UPDATE_BLOCKED", "updates_apply", "BLOCKED", "CRITICAL", "Security scan failed")
        await interaction.followup.send(
            embed=create_error_embed("❌ مرفوض", "فشل فحص الحماية"),
            ephemeral=True,
            allowed_mentions=SAFE_ALLOWED_MENTIONS
        )
        return
    
    integrity = integrity_service.run_integrity_check()
    if integrity["overall_status"] == "FAIL":
        log_panel_action(guild_id, user_id, "UPDATE_BLOCKED", "updates_apply", "BLOCKED", "CRITICAL", "Integrity check failed")
        await interaction.followup.send(
            embed=create_error_embed("❌ مرفوض", "فشل فحص Integrity"),
            ephemeral=True,
            allowed_mentions=SAFE_ALLOWED_MENTIONS
        )
        return
    
    success, msg = await update_service.apply_update()
    
    if success:
        log_panel_action(guild_id, user_id, "UPDATE_APPLY_CONFIRMED", "updates_apply", "SUCCESS", "HIGH")
        await alert_service.send_update_alert(msg)
        await interaction.followup.send(
            embed=create_success_embed("✅ تم", msg),
            ephemeral=True,
            allowed_mentions=SAFE_ALLOWED_MENTIONS
        )
    else:
        await interaction.followup.send(
            embed=create_error_embed("❌ خطأ", "فشل في التحديث"),
            ephemeral=True,
            allowed_mentions=SAFE_ALLOWED_MENTIONS
        )


async def cancel_update(interaction: discord.Interaction):
    await interaction.followup.send(
        embed=create_info_embed("ℹ️ تم الإلغاء", "تم إلغاء التحديث"),
        ephemeral=True,
        allowed_mentions=SAFE_ALLOWED_MENTIONS
    )


async def handle_settings_section(interaction: discord.Interaction, action: str):
    from src.ui.views.settings_view import SettingsView
    guild_id = str(interaction.guild_id) if interaction.guild else "0"
    user_id = str(interaction.user.id) if interaction.user else "0"
    
    if not check_permission(guild_id, user_id, "SETTINGS_VIEW"):
        await interaction.followup.send(
            embed=create_unauthorized_embed(),
            ephemeral=True,
            allowed_mentions=SAFE_ALLOWED_MENTIONS
        )
        return
    
    await interaction.followup.send(
        embed=create_section_embed("⚙️ الإعدادات"),
        view=SettingsView(user_id, guild_id),
        ephemeral=True,
        allowed_mentions=SAFE_ALLOWED_MENTIONS
    )


async def handle_alliance_section(interaction: discord.Interaction, action: str):
    from src.ui.views.alliance_view import AllianceView
    guild_id = str(interaction.guild_id) if interaction.guild else "0"
    user_id = str(interaction.user.id) if interaction.user else "0"
    lang = get_user_language(guild_id, user_id)
    
    if not check_permission(guild_id, user_id, "ALLIANCE_VIEW"):
        await interaction.followup.send(
            embed=create_unauthorized_embed(),
            ephemeral=True,
            allowed_mentions=SAFE_ALLOWED_MENTIONS
        )
        return
    
    await interaction.followup.send(
        embed=create_section_embed("🏰 " + t("alliance.title", lang)),
        view=AllianceView(user_id, guild_id, lang),
        ephemeral=True,
        allowed_mentions=SAFE_ALLOWED_MENTIONS
    )


async def handle_reminder_section(interaction: discord.Interaction, action: str):
    from src.ui.views.reminder_view import ReminderView
    guild_id = str(interaction.guild_id) if interaction.guild else "0"
    user_id = str(interaction.user.id) if interaction.user else "0"
    lang = get_user_language(guild_id, user_id)
    
    await interaction.followup.send(
        embed=create_section_embed("⏰ " + t("reminder.title", lang)),
        view=ReminderView(user_id, guild_id, lang),
        ephemeral=True,
        allowed_mentions=SAFE_ALLOWED_MENTIONS
    )


async def handle_player_id_section(interaction: discord.Interaction, action: str):
    from src.ui.views.reminder_view import PlayerIDSelfServiceView
    guild_id = str(interaction.guild_id) if interaction.guild else "0"
    user_id = str(interaction.user.id) if interaction.user else "0"
    lang = get_user_language(guild_id, user_id)
    
    await interaction.followup.send(
        embed=create_section_embed("🔑 " + t("player_id.title", lang)),
        view=PlayerIDSelfServiceView(user_id, guild_id, lang),
        ephemeral=True,
        allowed_mentions=SAFE_ALLOWED_MENTIONS
    )


async def handle_reminder_button(interaction: discord.Interaction, custom_id: str, guild_id: str, user_id: str, lang: str):
    from src.ui.modals.reminder_modals import CreateReminderModal, TimeSettingsModal
    from src.services.reminder_service import get_upcoming_reminders, delete_reminder
    import discord
    
    action = custom_id.split(":")[-1]
    
    if action == "create":
        modal = CreateReminderModal(user_id, guild_id, lang)
        await interaction.response.send_modal(modal)
        return
    
    if action == "settings":
        modal = TimeSettingsModal(user_id, guild_id, lang)
        await interaction.response.send_modal(modal)
        return
    
    if action == "upcoming":
        reminders = get_upcoming_reminders(guild_id, 10)
        if not reminders:
            desc = t("reminder.no_upcoming", lang)
        else:
            desc = "\n".join([f"• {r['event_name']} @ {r['event_time_local']}" for r in reminders])
        
        await interaction.response.send_message(
            embed=discord.Embed(
                title=t("reminder.upcoming", lang),
                description=desc,
                color=discord.Color.blue()
            ),
            ephemeral=True,
            allowed_mentions=SAFE_ALLOWED_MENTIONS
        )
        return
    
    if action == "delete":
        await interaction.response.send_message(
            embed=discord.Embed(
                title=t("reminder.delete", lang),
                description=t("reminder.delete_help", lang),
                color=discord.Color.orange()
            ),
            ephemeral=True,
            allowed_mentions=SAFE_ALLOWED_MENTIONS
        )
        return


async def handle_player_id_button(interaction: discord.Interaction, custom_id: str, guild_id: str, user_id: str, lang: str):
    from src.ui.modals.player_id_modals import RegisterPlayerIDModal, UpdatePlayerIDModal, DeletePlayerIDModal
    from src.services.player_id_service import get_player_id
    import discord
    
    action = custom_id.split(":")[-1]
    
    if action == "register":
        modal = RegisterPlayerIDModal(user_id, guild_id, lang)
        await interaction.response.send_modal(modal)
        return
    
    if action == "update":
        modal = UpdatePlayerIDModal(user_id, guild_id, lang)
        await interaction.response.send_modal(modal)
        return
    
    if action == "delete":
        modal = DeletePlayerIDModal(user_id, guild_id, lang)
        await interaction.response.send_modal(modal)
        return
    
    if action == "view":
        player = get_player_id(guild_id, user_id)
        if player:
            desc = f"**Player ID:** `{player['player_id']}`\n**Registered:** {player['created_at'][:10]}"
        else:
            desc = t("player_id.not_registered", lang)
        
        await interaction.response.send_message(
            embed=discord.Embed(
                title=t("player_id.my_id", lang),
                description=desc,
                color=discord.Color.blue()
            ),
            ephemeral=True,
            allowed_mentions=SAFE_ALLOWED_MENTIONS
        )
        return


async def run_cleanup(interaction: discord.Interaction):
    from src.services.cleanup_service import cleanup_service
    from src.ui.components.guards import log_panel_action
    
    guild_id = str(interaction.guild_id) if interaction.guild else "0"
    user_id = str(interaction.user.id) if interaction.user else "0"
    
    allowed, reason = await check_admin_permission(interaction, "cleanup")
    if not allowed:
        await interaction.followup.send(
            embed=create_unauthorized_embed(),
            ephemeral=True,
            allowed_mentions=SAFE_ALLOWED_MENTIONS
        )
        return
    
    log_panel_action(guild_id, user_id, "CLEANUP_RUN", "maintenance", "SUCCESS", "MEDIUM")
    await cleanup_service.run_once()
    await interaction.followup.send(
        embed=create_success_embed("✅ تم", "تم تنفيذ Cleanup"),
        ephemeral=True,
        allowed_mentions=SAFE_ALLOWED_MENTIONS
    )


async def run_retry(interaction: discord.Interaction):
    from src.services.retry_service import retry_service
    from src.ui.components.guards import log_panel_action
    
    guild_id = str(interaction.guild_id) if interaction.guild else "0"
    user_id = str(interaction.user.id) if interaction.user else "0"
    
    allowed, reason = await check_admin_permission(interaction, "retry")
    if not allowed:
        await interaction.followup.send(
            embed=create_unauthorized_embed(),
            ephemeral=True,
            allowed_mentions=SAFE_ALLOWED_MENTIONS
        )
        return
    
    log_panel_action(guild_id, user_id, "RETRY_RUN", "maintenance", "SUCCESS", "MEDIUM")
    await retry_service.run_once()
    await interaction.followup.send(
        embed=create_success_embed("✅ تم", "تم تنفيذ Retry Jobs"),
        ephemeral=True,
        allowed_mentions=SAFE_ALLOWED_MENTIONS
    )


async def show_logs_status(interaction: discord.Interaction):
    from src.utils.logger import bot_logger
    import logging
    
    logger_info = {
        "level": bot_logger.level,
        "name": bot_logger.name,
    }
    
    fields = [
        ("Logger Level", logging.getLevelName(logger_info["level"]), True),
        ("Logger Name", logger_info["name"], True),
    ]
    
    await interaction.followup.send(
        embed=create_field_embed("📄 Logs Status", fields),
        ephemeral=True,
        allowed_mentions=SAFE_ALLOWED_MENTIONS
    )


def get_section_title(section: str) -> str:
    titles = {
        "redeem": "🎁 الأكواد",
        "players": "👥 اللاعبين",
        "security": "🛡️ الحماية",
        "system": "⚙️ النظام",
        "backup": "💾 النسخ",
        "update": "🔄 التحديثات",
        "maintenance": "🧹 الصيانة",
    }
    return titles.get(section, section)
