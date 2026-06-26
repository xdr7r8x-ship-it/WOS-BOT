from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from .config import config
from .routes import auth_routes, dashboard_routes, gift_code_routes
from .routes import player_routes, player_panel_routes, alliance_routes
from .routes import reminder_routes, content_routes, admin_routes
from .routes import security_routes, system_routes, backup_routes
from .routes import update_routes, audit_routes, alliance_api_routes


def init_database_tables():
    from database import get_db
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS web_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id_hash TEXT NOT NULL UNIQUE,
                guild_id TEXT,
                user_id TEXT NOT NULL,
                role_level TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                created_at TEXT NOT NULL,
                last_seen_at TEXT NOT NULL,
                revoked INTEGER NOT NULL DEFAULT 0
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS web_audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id TEXT,
                actor_id TEXT NOT NULL,
                action TEXT NOT NULL,
                target TEXT,
                result TEXT NOT NULL,
                risk_level TEXT NOT NULL DEFAULT 'LOW',
                ip_hash TEXT,
                user_agent_hash TEXT,
                metadata TEXT,
                created_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS web_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id TEXT NOT NULL UNIQUE,
                dashboard_enabled INTEGER NOT NULL DEFAULT 1,
                default_language TEXT NOT NULL DEFAULT 'ar',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        conn.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_database_tables()
    yield


app = FastAPI(
    title="WOS-BOT Web Dashboard",
    description="Web Dashboard for Whiteout Survival Discord Bot",
    version="1.0.0",
    lifespan=lifespan,
)

if config.WEB_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.WEB_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(auth_routes.router)
app.include_router(dashboard_routes.router)
app.include_router(gift_code_routes.router)
app.include_router(player_routes.router)
app.include_router(player_panel_routes.router)
app.include_router(alliance_routes.router)
app.include_router(alliance_api_routes.router)
app.include_router(reminder_routes.router)
app.include_router(content_routes.router)
app.include_router(admin_routes.router)
app.include_router(security_routes.router)
app.include_router(system_routes.router)
app.include_router(backup_routes.router)
app.include_router(update_routes.router)
app.include_router(audit_routes.router)


@app.get("/")
async def root():
    return {"message": "WOS-BOT Web Dashboard API", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
