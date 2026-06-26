from fastapi import WebSocket, WebSocketDisconnect, Request
from typing import Dict, Set
import asyncio
import json
from datetime import datetime

from .session import get_session_manager
from .config import config


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = set()
        self.active_connections[session_id].add(websocket)

    def disconnect(self, websocket: WebSocket, session_id: str):
        if session_id in self.active_connections:
            self.active_connections[session_id].discard(websocket)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]

    async def broadcast(self, session_id: str, message: dict):
        if session_id in self.active_connections:
            for connection in self.active_connections[session_id]:
                try:
                    await connection.send_json(message)
                except:
                    pass


manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket):
    session_id = websocket.cookies.get(config.WEB_COOKIE_NAME)
    
    if not session_id:
        await websocket.close(code=4001, reason="Authentication required")
        return
    
    session_manager = get_session_manager()
    session = session_manager.validate_session(session_id)
    
    if not session:
        await websocket.close(code=4001, reason="Session expired")
        return
    
    await manager.connect(websocket, session_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            elif message.get("type") == "subscribe":
                channel = message.get("channel")
                await websocket.send_json({
                    "type": "subscribed",
                    "channel": channel,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id)


async def broadcast_bot_status(status: dict):
    for session_id in manager.active_connections:
        await manager.broadcast(session_id, {
            "type": "bot_status",
            "data": status,
            "timestamp": datetime.utcnow().isoformat()
        })


async def broadcast_queue_update(queue: list):
    for session_id in manager.active_connections:
        await manager.broadcast(session_id, {
            "type": "queue_update",
            "data": {"queue": queue},
            "timestamp": datetime.utcnow().isoformat()
        })
