from collections import defaultdict

from fastapi import WebSocket
from app.core.logger import log_info

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = defaultdict(list)

    async def connect(self, group_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[group_id].append(websocket)

    def disconnect(self, group_id: str, websocket: WebSocket):
        connections = self.active_connections.get(group_id, [])

        if websocket in connections:
            connections.remove(websocket)

        if not connections:
            self.active_connections.pop(group_id, None)

    async def send_personal_message(
        self,
        websocket: WebSocket,
        message: dict,
    ):
        await websocket.send_json(message)

    async def broadcast(self, group_id: str, message: dict):
        connections = self.active_connections.get(group_id, [])

        # log_info(f"==========================================")
        # log_info("Broadcast group:", group_id)
        # log_info("Connected clients:", len(connections))
        # log_info(f"==========================================")
        for websocket in connections.copy():
            try:
                await websocket.send_json(message)
                log_info("WebSocket message sent successfully")
            except Exception as e:
                log_info(f"WebSocket broadcast failed: {repr(e)}")
                self.disconnect(group_id, websocket)

    async def broadcast_except(
        self,
        group_id: str,
        excluded_websocket: WebSocket,
        message: dict,
    ):
        connections = self.active_connections.get(group_id, [])

        for websocket in connections.copy():
            if websocket is excluded_websocket:
                continue
            try:
                await websocket.send_json(message)
            except Exception:
                self.disconnect(group_id, websocket)

    async def close_connection(
        self,
        group_id: str,
        websocket: WebSocket,
        code: int = 1000,
    ):
        self.disconnect(group_id, websocket)

        try:
            await websocket.close(code=code)
        except Exception:
            pass


manager = ConnectionManager()