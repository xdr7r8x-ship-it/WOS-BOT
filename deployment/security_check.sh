#!/bin/bash
# WOS-BOT Security Check Script
# Verifies security settings and secrets

echo "=========================================="
echo "WOS-BOT Security Check"
echo "=========================================="

PASS=0
FAIL=0

echo ""
echo "[1/12] Checking .env file permissions..."
if [ -f "/opt/wos-bot/.env" ]; then
    PERMS=$(stat -c %a /opt/wos-bot/.env)
    if [ "$PERMS" = "600" ]; then
        echo "  ✓ PASS: .env permissions are 600"
        ((PASS++))
    else
        echo "  ✗ FAIL: .env permissions are $PERMS (should be 600)"
        ((FAIL++))
    fi
else
    echo "  ✗ FAIL: .env not found"
    ((FAIL++))
fi

echo ""
echo "[2/12] Checking .env file ownership..."
if [ -f "/opt/wos-bot/.env" ]; then
    OWNER=$(stat -c %U /opt/wos-bot/.env)
    if [ "$OWNER" = "wosbot" ]; then
        echo "  ✓ PASS: .env owned by wosbot"
        ((PASS++))
    else
        echo "  ✗ FAIL: .env owned by $OWNER (should be wosbot)"
        ((FAIL++))
    fi
else
    echo "  ✗ FAIL: .env not found"
    ((FAIL++))
fi

echo ""
echo "[3/12] Checking service file permissions..."
SERVICE_PERMS=$(stat -c %a /etc/systemd/system/wos-bot.service 2>/dev/null || echo "0")
if [ "$SERVICE_PERMS" = "644" ] || [ "$SERVICE_PERMS" = "755" ]; then
    echo "  ✓ PASS: Service file permissions OK"
    ((PASS++))
else
    echo "  ✗ FAIL: Service file permissions are $SERVICE_PERMS"
    ((FAIL++))
fi

echo ""
echo "[4/12] Checking NoNewPrivileges in service..."
if grep -q "NoNewPrivileges=true" /etc/systemd/system/wos-bot.service 2>/dev/null; then
    echo "  ✓ PASS: NoNewPrivileges enabled"
    ((PASS++))
else
    echo "  ✗ FAIL: NoNewPrivileges not enabled"
    ((FAIL++))
fi

echo ""
echo "[5/12] Checking PrivateTmp in service..."
if grep -q "PrivateTmp=true" /etc/systemd/system/wos-bot.service 2>/dev/null; then
    echo "  ✓ PASS: PrivateTmp enabled"
    ((PASS++))
else
    echo "  ✗ FAIL: PrivateTmp not enabled"
    ((FAIL++))
fi

echo ""
echo "[6/12] Checking ProtectSystem in service..."
if grep -q "ProtectSystem=full" /etc/systemd/system/wos-bot.service 2>/dev/null; then
    echo "  ✓ PASS: ProtectSystem enabled"
    ((PASS++))
else
    echo "  ✗ FAIL: ProtectSystem not enabled"
    ((FAIL++))
fi

echo ""
echo "[7/12] Checking ProtectHome in service..."
if grep -q "ProtectHome=true" /etc/systemd/system/wos-bot.service 2>/dev/null; then
    echo "  ✓ PASS: ProtectHome enabled"
    ((PASS++))
else
    echo "  ✗ FAIL: ProtectHome not enabled"
    ((FAIL++))
fi

echo ""
echo "[8/12] Checking database file..."
if [ -f "/opt/wos-bot/db/wos_bot.sqlite3" ]; then
    echo "  ✓ PASS: Database file exists"
    ((PASS++))
else
    echo "  ✗ FAIL: Database file not found"
    ((FAIL++))
fi

echo ""
echo "[9/12] Checking for exposed secrets in files..."
SECRETS_FOUND=0
for file in /opt/wos-bot/*.py; do
    if grep -l "DISCORD_BOT_TOKEN\s*=\s*['\"][^'\"]{10,}['\"]" "$file" 2>/dev/null; then
        echo "  ✗ FAIL: Possible token in $file"
        ((FAIL++))
        SECRETS_FOUND=1
    fi
done
if [ $SECRETS_FOUND -eq 0 ]; then
    echo "  ✓ PASS: No obvious secrets found in code"
    ((PASS++))
fi

echo ""
echo "[10/12] Checking logs for secrets..."
if [ -d "/opt/wos-bot/logs" ]; then
    SECRET_LOGS=$(grep -r "Bearer\|Token\|API_KEY\|password" /opt/wos-bot/logs/*.log 2>/dev/null | grep -v "REDACTED" | head -1 || true)
    if [ -z "$SECRET_LOGS" ]; then
        echo "  ✓ PASS: No obvious secrets in logs"
        ((PASS++))
    else
        echo "  ✗ FAIL: Possible secret in logs"
        ((FAIL++))
    fi
else
    echo "  ✓ PASS: No logs directory"
    ((PASS++))
fi

echo ""
echo "[11/12] Checking backup directory..."
if [ -d "/opt/wos-bot/backups" ]; then
    ENV_IN_BACKUP=$(find /opt/wos-bot/backups -name ".env" 2>/dev/null | head -1 || true)
    if [ -z "$ENV_IN_BACKUP" ]; then
        echo "  ✓ PASS: No .env in backups"
        ((PASS++))
    else
        echo "  ⚠️  WARNING: .env found in backups (should be excluded)"
        ((FAIL++))
    fi
else
    echo "  ✓ PASS: No backups directory"
    ((PASS++))
fi

echo ""
echo "[12/12] Checking user permissions..."
BOT_USER_HOME=$(getent passwd wosbot | cut -d: -f6)
if [ "$BOT_USER_HOME" = "/opt/wos-bot" ]; then
    echo "  ✓ PASS: wosbot home directory set correctly"
    ((PASS++))
else
    echo "  ✗ FAIL: wosbot home directory is $BOT_USER_HOME"
    ((FAIL++))
fi

echo ""
echo "=========================================="
echo "Security Check Results"
echo "=========================================="
echo "Passed: $PASS"
echo "Failed: $FAIL"
echo ""

if [ $FAIL -eq 0 ]; then
    echo "✓ All security checks passed!"
    exit 0
else
    echo "✗ Some security checks failed. Please review."
    exit 1
fi
