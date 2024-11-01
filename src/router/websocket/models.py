from fastapi import WebSocket
from fastapi.websockets import WebSocketState
from pydantic import BaseModel


class WS(BaseModel):
    client_id: str
    websocket: WebSocket

    class Config:
        arbitrary_types_allowed = True


class ConnectManager:
    def __init__(self) -> None:
        self.activate_connections: list[WS] = []
        self.rooms: dict[str, ConnectManager] = {}

    async def connect(
        self,
        websocket: WebSocket,
        client_id: str,
        room_id: str | None = None,
    ):
        if room_id:
            if room_id not in self.rooms:
                self.rooms[room_id] = ConnectManager()
            await self.rooms[room_id].connect(websocket, client_id)
        else:
            await websocket.accept()
            if client_id in [w.client_id for w in self.activate_connections]:
                self.disconnect(client_id)
            self.activate_connections.append(
                WS(client_id=client_id, websocket=websocket)
            )

    def disconnect(self, client_id: str):
        """
        Disconnect websocket from manager
        """
        for w in self.activate_connections:
            if w.client_id == client_id:
                self.activate_connections.remove(w)
                break
        else:
            for room in self.rooms.values():
                room.disconnect(client_id)

    async def send_personal_message(
        self, websocket: WebSocket, client_id: str, message: str
    ):
        for w in self.activate_connections:
            if w.client_id == client_id:
                await w.websocket.send_text(message)
                break
        else:
            for room in self.rooms.values():
                await room.send_personal_message(websocket, client_id, message)

    async def broadcast(
        self, websocket: WebSocket, message: str, room_id: str | None = None
    ):
        if room_id:
            if room_id in self.rooms:
                await self.rooms[room_id].broadcast(websocket, message)
        else:
            for w in self.activate_connections:
                if w.websocket == websocket:
                    continue
                if w.websocket.client_state == WebSocketState.CONNECTED:
                    await w.websocket.send_text(message)

    def get_all_clients(self, room_id: str | None = None) -> list[WS]:
        if room_id:
            if room_id in self.rooms:
                return self.rooms[room_id].get_all_clients()
        else:
            return self.activate_connections
        return []
