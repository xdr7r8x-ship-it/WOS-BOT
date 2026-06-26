import uvicorn
from .app import app
from .websocket import websocket_endpoint
from fastapi import WebSocket
from fastapi.routing import APIRoute
from typing import Callable
from starlette.routing import Route, WebSocketRoute


class CustomRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request):
            try:
                return await original_route_handler(request)
            except Exception as e:
                from fastapi.responses import JSONResponse
                return JSONResponse(
                    status_code=500,
                    content={"detail": "Internal server error"}
                )

        return custom_route_handler


app.router.route_class = CustomRoute


async def websocket_route(websocket: WebSocket):
    await websocket_endpoint(websocket)


app.add_websocket_route("/ws/live", websocket_route)


if __name__ == "__main__":
    from .config import config
    
    uvicorn.run(
        "src.web.backend.main:app",
        host=config.WEB_DASHBOARD_HOST,
        port=config.WEB_DASHBOARD_PORT,
        reload=False,
        log_level="info",
    )
