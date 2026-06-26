#!/bin/bash
# WOS-BOT Rollback Script
# Restores the bot to a previous backup

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <timestamp>"
    echo "Example: $0 20240626_120000"
    exit 1
fi

TIMESTAMP="$1"
BOT_DIR="/opt/wos-bot"
RELEASE_DIR="$BOT_DIR/releases"
BACKUP_PATH="$RELEASE_DIR/wos_backup_$TIMESTAMP"

echo "=========================================="
echo "WOS-BOT Rollback Script"
echo "=========================================="

if [ ! -d "$BACKUP_PATH" ]; then
    echo "Error: Backup not found at $BACKUP_PATH"
    exit 1
fi

echo "[1/4] Stopping bot..."
systemctl stop wos-bot
echo "  ✓ Bot stopped"

echo "[2/4] Restoring database..."
cp "$BACKUP_PATH/wos_bot.sqlite3" "$BOT_DIR/db/" 2>/dev/null || true
echo "  ✓ Database restored"

echo "[3/4] Restoring configuration..."
cp "$BACKUP_PATH/.env" "$BOT_DIR/" 2>/dev/null || true
echo "  ✓ Configuration restored"

echo "[4/4] Starting bot..."
systemctl start wos-bot
sleep 3
systemctl status wos-bot --no-pager || true

echo ""
echo "=========================================="
echo "Rollback Complete!"
echo "=========================================="
