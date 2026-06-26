#!/bin/bash
set -e

echo "=== WOS-BOT Dashboard Deployment ==="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "1. Installing Python dependencies..."
pip install -r requirements.txt

echo "2. Installing frontend dependencies..."
cd src/web/frontend
npm install

echo "3. Building frontend..."
npm run build

cd "$PROJECT_DIR"

echo "4. Creating directories..."
mkdir -p db logs backups releases

echo "5. Copying systemd service..."
sudo cp deployment/wos-dashboard.service /etc/systemd/system/

echo "6. Reloading systemd..."
sudo systemctl daemon-reload

echo "7. Enabling service..."
sudo systemctl enable wos-dashboard

echo "8. Starting service..."
sudo systemctl restart wos-dashboard

echo ""
echo "=== Deployment Complete ==="
echo "Dashboard: http://localhost:8080"
echo ""
echo "To setup Nginx:"
echo "  sudo cp deployment/nginx-wos-dashboard.conf /etc/nginx/sites-available/"
echo "  sudo ln -s /etc/nginx/sites-available/nginx-wos-dashboard.conf /etc/nginx/sites-enabled/"
echo "  sudo nginx -t && sudo systemctl reload nginx"
