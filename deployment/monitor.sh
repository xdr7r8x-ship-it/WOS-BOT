#!/bin/bash
# WOS-BOT Monitoring Script
# Run to check bot health and view logs

echo "=========================================="
echo "WOS-BOT Status Monitor"
echo "=========================================="

echo ""
echo "[1/6] Systemd Service Status:"
echo "----------------------------------------"
systemctl status wos-bot --no-pager || true

echo ""
echo "[2/6] Bot Uptime:"
echo "----------------------------------------"
systemctl show wos-bot --property=ActiveEnterTimestamp --value

echo ""
echo "[3/6] Restart Count (last 24h):"
echo "----------------------------------------"
journalctl -u wos-bot --since "24 hours ago" --no-pager | grep -c "Started wos-bot" || echo "0 restarts"

echo ""
echo "[4/6] Recent Logs (last 20 lines):"
echo "----------------------------------------"
journalctl -u wos-bot -n 20 --no-pager

echo ""
echo "[5/6] Database Size:"
echo "----------------------------------------"
ls -lh /opt/wos-bot/db/wos_bot.sqlite3 2>/dev/null || echo "Database not found"

echo ""
echo "[6/6] Disk Usage:"
echo "----------------------------------------"
du -sh /opt/wos-bot/

echo ""
echo "=========================================="
echo "To view live logs: journalctl -u wos-bot -f"
echo "To stop bot: systemctl stop wos-bot"
echo "To restart bot: systemctl restart wos-bot"
echo "=========================================="
