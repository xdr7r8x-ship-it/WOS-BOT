# VPS Deployment Guide

## Prerequisites

- Ubuntu/Debian VPS with sudo access
- Git installed
- Python 3.11+
- Node.js 18+ (for frontend)
- Nginx installed
- Cloudflare Tunnel (optional, for temporary domain)

---

## Step 1: Clone Repository

```bash
cd /opt
git clone https://github.com/xdr7r8x-ship-it/WOS-BOT.git wos-bot
cd /opt/wos-bot
```

---

## Step 2: Configure Environment

```bash
cp .env.example .env 2>/dev/null || touch .env
nano .env
```

### Required .env Configuration

```env
DISCORD_BOT_TOKEN=YOUR_BOT_TOKEN
BOT_OWNER_IDS=YOUR_DISCORD_USER_ID

WEB_DASHBOARD_ENABLED=true
WEB_PUBLIC_URL=https://YOUR_DOMAIN
WEB_DASHBOARD_HOST=127.0.0.1
WEB_DASHBOARD_PORT=8080

DISCORD_OAUTH_CLIENT_ID=1519806811744632994
DISCORD_OAUTH_CLIENT_SECRET=YOUR_CLIENT_SECRET
DISCORD_OAUTH_REDIRECT_URI=https://YOUR_DOMAIN/api/v1/auth/discord/callback

WEB_SESSION_SECRET=openssl rand -hex 32
WEB_COOKIE_SECURE=true
WEB_CORS_ORIGINS=https://YOUR_DOMAIN

WOS_API_KEY=openssl rand -hex 32
```

---

## Step 3: Option A - Cloudflare Quick Tunnel (Temporary)

If you don't have a domain, use Cloudflare Quick Tunnel:

```bash
# Install cloudflared
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o /usr/local/bin/cloudflared
chmod +x /usr/local/bin/cloudflared

# Run tunnel in background
cloudflared tunnel --url http://localhost:8080 &
```

Note the generated URL (e.g., `https://xxxx.trycloudflare.com`) and use it as your domain.

### Update .env for Cloudflare Tunnel

```env
WEB_PUBLIC_URL=https://GENERATED.trycloudflare.com
DISCORD_OAUTH_REDIRECT_URI=https://GENERATED.trycloudflare.com/api/v1/auth/discord/callback
WEB_COOKIE_SECURE=true
WEB_CORS_ORIGINS=https://GENERATED.trycloudflare.com
```

> ⚠️ Cloudflare Quick Tunnel is temporary and may change after restart.
> For production, use a stable domain.

---

## Step 4: Option B - DuckDNS (Free Domain)

```bash
# Register at https://www.duckdns.org
# Get your token from the dashboard
# Choose a subdomain

# Install ddclient
sudo apt install ddclient

# Configure /etc/ddclient.conf
echo 'daemon=300
ssl=yes
protocol=duckdns
login=YOUR_EMAIL
password=YOUR_TOKEN
YOUR_SUBDOMAIN.duckdns.org' | sudo tee /etc/ddclient.conf

sudo systemctl enable ddclient
sudo systemctl start ddclient
```

---

## Step 5: Discord Developer Portal Setup

1. Go to https://discord.com/developers/applications
2. Open your application
3. Go to OAuth2 settings
4. Add redirect URI:
   ```
   https://YOUR_DOMAIN/api/v1/auth/discord/callback
   ```
5. Copy Client ID and Client Secret
6. Add Client Secret to .env

---

## Step 6: Deploy Bot

```bash
cd /opt/wos-bot
sudo bash deployment/deploy.sh
```

---

## Step 7: Deploy Dashboard

```bash
sudo bash deployment/dashboard_deploy.sh
```

---

## Step 8: Configure Nginx

```bash
# Copy nginx config
sudo cp deployment/nginx-wos-dashboard.conf /etc/nginx/sites-available/wos-dashboard
sudo ln -sf /etc/nginx/sites-available/wos-dashboard /etc/nginx/sites-enabled/

# Edit config with your domain
sudo nano /etc/nginx/sites-available/wos-dashboard

# Test and reload
sudo nginx -t
sudo systemctl reload nginx
```

---

## Step 9: Start Services

```bash
sudo systemctl daemon-reload
sudo systemctl enable wos-bot wos-dashboard
sudo systemctl restart wos-bot wos-dashboard
```

---

## Step 10: Verify Services

```bash
sudo systemctl status wos-bot --no-pager
sudo systemctl status wos-dashboard --no-pager
```

---

## Step 11: Check Logs

```bash
journalctl -u wos-bot -n 100 --no-pager
journalctl -u wos-dashboard -n 100 --no-pager
```

---

## Step 12: Test Functionality

### Bot Commands
```
/wos
/playerid register <player_id>
/alliance set <alliance_name>
/reminder set <minutes>
```

### Dashboard
1. Open https://YOUR_DOMAIN
2. Click "Login with Discord"
3. Authorize application
4. Select guild

---

## Troubleshooting

### Bot not starting
```bash
journalctl -u wos-bot -n 50 --no-pager
# Check for missing dependencies or config errors
```

### Dashboard 502 Bad Gateway
```bash
sudo systemctl status wos-dashboard
sudo systemctl restart wos-dashboard
```

### Nginx SSL issues
```bash
sudo certbot --nginx -d YOUR_DOMAIN
```

---

## Security Notes

- Never commit .env to GitHub
- Use strong secrets: `openssl rand -hex 32`
- Enable firewall: `sudo ufw allow 22 && sudo ufw allow 443`
- Keep system updated: `sudo apt update && sudo apt upgrade`

---

## Files Protected by .gitignore

```
.env
.env.*
*.db
logs/
*.log
.venv/
venv/
```

---

## Service Management

```bash
# Restart bot
sudo systemctl restart wos-bot

# Restart dashboard
sudo systemctl restart wos-dashboard

# View real-time logs
journalctl -u wos-bot -f
journalctl -u wos-dashboard -f

# Stop services
sudo systemctl stop wos-bot wos-dashboard
```
