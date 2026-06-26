# Whiteout Survival Gift Code Bot

A Discord bot for automated gift code redemption in Whiteout Survival.

## Features

- **Auto-detection**: Automatically detects gift codes in configured channels
- **Auto-redeem**: Redeems codes for all registered players
- **User Registration**: Players can register their in-game FID
- **Slash Commands**: `/setup`, `/redeem`, `/status`, `/players`
- **SQLite Storage**: All data persisted locally

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

3. Add your Discord bot token to `.env`:
```
DISCORD_BOT_TOKEN=your_bot_token_here
```

4. Run the bot:
```bash
python main.py
```

## Commands

- `/setup` - Configure register and codes channels
- `/redeem <code>` - Manually redeem a gift code
- `/status <code>` - Check redemption status
- `/players` - List all registered players

## Channel Setup

1. Use `/setup` command
2. Select the **Register Channel** - where players send their FID to register
3. Select the **Codes Channel** - where gift codes will be auto-detected
4. Click **Save Settings**

## Player Registration

In the register channel, send your game FID:
```
12345678
```
Or with nickname:
```
12345678 MyNickname
```

## Project Structure

```
WOS-BOT/
├── main.py                 # Bot entry point
├── database.py             # SQLite database operations
├── requirements.txt        # Dependencies
├── .env.example           # Environment template
├── db/                    # SQLite database files (created at runtime)
└── src/
    ├── api/
    │   └── redeem.py      # Whiteout API client
    ├── utils/
    │   ├── sign.py        # Sign generation utilities
    │   ├── captcha.py     # Captcha solver (mock if no API key)
    │   └── request.py     # HTTP request utilities
    └── services/
        └── redeem_service.py  # Redemption service layer
```
