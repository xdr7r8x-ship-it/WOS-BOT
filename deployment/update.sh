#!/bin/bash
# WOS-BOT Update Script
# Updates the bot with a new version

set -e

BOT_DIR="/opt/wos-bot"
RELEASE_DIR="$BOT_DIR/releases"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="wos_backup_$TIMESTAMP"

echo "=========================================="
echo "WOS-BOT Update Script"
echo "=========================================="

echo "[1/7] Creating backup..."
mkdir -p "$RELEASE_DIR/$BACKUP_NAME"
cp -r "$BOT_DIR/db" "$RELEASE_DIR/$BACKUP_NAME/" 2>/dev/null || true
cp "$BOT_DIR/.env" "$RELEASE_DIR/$BACKUP_NAME/" 2>/dev/null || true
echo "  ✓ Backup saved to $RELEASE_DIR/$BACKUP_NAME"

echo "[2/7] Stopping bot..."
systemctl stop wos-bot
echo "  ✓ Bot stopped"

echo "[3/7] Waiting for graceful shutdown..."
sleep 5

echo "[4/7] Updating files..."
rsync -av --exclude='.env' \
           --exclude='__pycache__' \
           --exclude='.pytest_cache' \
           --exclude='.git' \
           --exclude='node_modules' \
           --exclude='db/*.sqlite3' \
           --exclude='logs/*.log' \
           --exclude='backups/*' \
           --exclude='deployment/' \
           /workspace/project/WOS-BOT/ "$BOT_DIR/"
echo "  ✓ Files updated"

echo "[5/7] Updating dependencies..."
cd "$BOT_DIR"
source .venv/bin/activate
pip install -r requirements.txt -q
echo "  ✓ Dependencies updated"

echo "[6/7] Running tests..."
python -m compileall . -q
echo "  ✓ compileall passed"

echo "[7/7] Starting bot..."
systemctl start wos-bot
sleep 3
systemctl status wos-bot --no-pager || true

echo ""
echo "=========================================="
echo "Update Complete!"
echo "=========================================="
echo ""
echo "To rollback: sudo bash deployment/rollback.sh $TIMESTAMP"
