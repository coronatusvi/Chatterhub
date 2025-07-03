from dataclasses import dataclass
import uuid
import json
from datetime import datetime
from db.database import SessionLocal
from db.models import Message

@dataclass
class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: dict = {}

    async def connect(self, websocket):
        await websocket.accept()
        id = str(uuid.uuid4())
        self.active_connections[id] = websocket

        username = websocket.cookies.get("username") or "Someone has"
        now = datetime.now().strftime("%H:%M:%S %d/%m/%Y")
        join_message = f"{username} joined at {now}"

        db = SessionLocal()
        existed = db.query(Message).filter(
            Message.username == "Admin",
            Message.content.like(f"{username} joined at%")
        ).first()

        if not existed:
            msg = Message(username="Admin", content=join_message)
            db.add(msg)
            db.commit()
            await self.broadcast(websocket, json.dumps({
                "username": "Admin",
                "message": join_message
            }))
        db.close()

    async def send_message(self, ws, message: str):
        await ws.send_text(message)

    def find_connection_id(self, websocket):
        websocket_list = list(self.active_connections.values())
        id_list = list(self.active_connections.keys())
        pos = websocket_list.index(websocket)
        return id_list[pos]

    async def broadcast(self, webSocket, data: str):
        decoded_data = json.loads(data)
        for connection in self.active_connections.values():
            is_me = (connection == webSocket)
            await connection.send_text(json.dumps({
                "isMe": is_me,
                "data": decoded_data['message'],
                "username": decoded_data['username']
            }))

    def disconnect(self, websocket):
        id = self.find_connection_id(websocket)
        del self.active_connections[id]
        return id