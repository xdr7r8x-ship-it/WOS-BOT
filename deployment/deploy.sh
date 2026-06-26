#!/bin/bash
# WOS-BOT VPS Deployment Script
# Run as root or with sudo

set -e

echo "=========================================="
echo "WOS-BOT VPS Deployment Script"
echo "=========================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root or with sudo"
    exit 1
fi

# Variables
BOT_DIR="/opt/wos-bot"
BOT_USER="wosbot"
BOT_GROUP="wosbot"

echo "[1/12] Creating directory structure..."
mkdir -p "$BOT_DIR"/{db,logs,backups,releases}
echo "  ✓ Directories created at $BOT_DIR"

echo "[2/12] Creating system user..."
useradd --system --home "$BOT_DIR" --shell /usr/sbin/nologin "$BOT_USER" 2>/dev/null || true
echo "  ✓ User '$BOT_USER' ready"

echo "[3/12] Setting permissions..."
chown -R "$BOT_USER:$BOT_GROUP" "$BOT_DIR"
chmod -R 750 "$BOT_DIR"
echo "  ✓ Permissions set"

echo "[4/12] Copying project files..."
# Exclude sensitive files
rsync -av --exclude='.env' \
           --exclude='__pycache__' \
           --exclude='.pytest_cache' \
           --exclude='.git' \
           --exclude='node_modules' \
           --exclude='*.pyc' \
           --exclude='db/*.sqlite3' \
           --exclude='logs/*.log' \
           --exclude='backups/*' \
           --exclude='deployment/' \
           /workspace/project/WOS-BOT/ "$BOT_DIR/"
echo "  ✓ Project files copied"

echo "[5/12] Creating Python virtual environment..."
cd "$BOT_DIR"
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "  ✓ Virtual environment ready"

echo "[6/12] Creating .env file..."
if [ ! -f "$BOT_DIR/.env" ]; then
    cp /workspace/project/WOS-BOT/deployment/.env.production "$BOT_DIR/.env"
    echo "  ⚠️  Please edit $BOT_DIR/.env and add your DISCORD_BOT_TOKEN"
else
    echo "  ✓ .env already exists, skipping"
fi

echo "[7/12] Setting .env permissions..."
chown "$BOT_USER:$BOT_GROUP" "$BOT_DIR/.env"
chmod 600 "$BOT_DIR/.env"
echo "  ✓ .env permissions set"

echo "[8/12] Installing systemd service..."
cp /workspace/project/WOS-BOT/deployment/wos-bot.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable wos-bot
echo "  ✓ Systemd service installed"

echo "[9/12] Running compileall..."
cd "$BOT_DIR"
source .venv/bin/activate
python -m compileall . -q
echo "  ✓ compileall passed"

echo "[10/12] Running pytest..."
python -m pytest tests/ -q --tb=short
echo "  ✓ pytest passed"

echo "[11/12] Clearing old Discord commands..."
CONFIRM_CLEAR_COMMANDS=true python scripts/clear_old_commands.py
echo "  ✓ Old commands cleared"

echo "[12/12] Starting bot service..."
systemctl start wos-bot
sleep 5
systemctl status wos-bot --no-pager || true

echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit $BOT_DIR/.env and add your DISCORD_BOT_TOKEN"
echo "2. Restart the bot: systemctl restart wos-bot"
echo "3. Check status: systemctl status wos-bot"
echo "4. View logs: journalctl -u wos-bot -f"
echo ""
