# WOS-BOT - Whiteout Survival Discord Bot

A powerful Discord bot for Whiteout Survival game management with a single `/wos` command interface.

## Features

- **Single Command**: `/wos` - Access all features through one unified panel
- **Gift Codes**: Auto-detect and redeem codes for all registered players
- **Player ID**: Self-service player ID management
- **Alliance**: Manage alliance information and sync
- **Reminders**: Create event reminders with game/real time support
- **Security**: Built-in abuse guard, secret scanner, input validation
- **I18N**: Arabic and English support
- **RBAC**: Role-based access control (Owner/Admin/Supervisor/Member)
- **SQLite**: All data persisted locally

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

3. Configure `.env`:
```
DISCORD_BOT_TOKEN=your_bot_token_here
WOS_API_KEY=your_wos_api_key_here
OWNER_ID=your_discord_user_id
```

4. Run the bot:
```bash
python main.py
```

## Commands

### Main Command
- `/wos` - Open the main control panel (single command for everything)

### Admin Commands
- `/wos` - Panel with all features accessible based on role

## Roles & Permissions

| Role | Access |
|------|--------|
| Owner | Full access to all features |
| Admin | Most features + user management |
| Supervisor | Basic features + monitoring |
| Member | Self-service features only |

## Project Structure

```
WOS-BOT/
├── main.py                      # Bot entry point
├── database.py                   # SQLite database operations
├── requirements.txt             # Dependencies
├── .env.example                 # Environment template
├── src/
│   ├── api/
│   │   ├── alliance_client.py   # Alliance API client
│   │   └── redeem.py            # Whiteout API client
│   ├── features/
│   │   └── */feature_manifest.py # Feature definitions
│   ├── services/
│   │   ├── feature_registry_service.py  # Feature registry
│   │   └── redeem_service.py            # Redemption service
│   ├── ui/
│   │   ├── wos_panel.py         # Main /wos panel
│   │   └── views/               # UI components
│   └── utils/
│       ├── rbac.py              # Role-based access control
│       └── i18n/                 # Translations
└── tests/                       # Unit tests
```

## Requirements

- Python 3.10+
- Discord.py 2.0+
- SQLite3

## License

MIT
