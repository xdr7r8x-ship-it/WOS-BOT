#!/bin/bash
# WOS-BOT Backup Script
# Creates a timestamped backup of database and configs

set -e

BOT_DIR="/opt/wos-bot"
BACKUP_DIR="$BOT_DIR/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="wos_backup_$TIMESTAMP"
BACKUP_PATH="$BACKUP_DIR/$BACKUP_NAME"

echo "=========================================="
echo "WOS-BOT Backup Script"
echo "=========================================="

mkdir -p "$BACKUP_PATH"

echo "[1/4] Backing up database..."
cp "$BOT_DIR/db/wos_bot.sqlite3" "$BACKUP_PATH/wos_bot.sqlite3" 2>/dev/null || true

echo "[2/4] Backing up configuration..."
cp "$BOT_DIR/.env" "$BACKUP_PATH/.env" 2>/dev/null || true
chmod 600 "$BACKUP_PATH/.env"

echo "[3/4] Compressing backup..."
cd "$BACKUP_DIR"
tar -czf "$BACKUP_NAME.tar.gz" "$BACKUP_NAME"
rm -rf "$BACKUP_NAME"

echo "[4/4] Cleaning old backups..."
cd "$BACKUP_DIR"
ls -t wos_backup_*.tar.gz | tail -n +11 | xargs -r rm -f

echo ""
echo "Backup created: $BACKUP_DIR/$BACKUP_NAME.tar.gz"
echo "Total backups: $(ls -t wos_backup_*.tar.gz | wc -l)"

echo ""
echo "=========================================="
echo "Backup Complete!"
echo "=========================================="
