from datetime import datetime

from fastapi import FastAPI, WebSocket
from fastapi.templating import Jinja2Templates
from dataclasses import dataclass
from typing import Dict
import uuid
import json
from db.database import SessionLocal
from fastapi.staticfiles import StaticFiles
from db.models import Message, User
import controllers.auth_controller as auth_router
import controllers.chat_controller as chat_router

templates = Jinja2Templates(directory="templates")

@dataclass
class ConnectionManager:
  def __init__(self) -> None:
    self.active_connections: dict = {}

  async def connect(self, websocket: WebSocket):
    await websocket.accept()
    id = str(uuid.uuid4())
    self.active_connections[id] = websocket

    print(f"username", websocket.cookies.get("username"))
    username = websocket.cookies.get("username") or "Someone has"
    now = datetime.now().strftime("%H:%M:%S %d/%m/%Y")
    join_message = f"{username} joined at {now}"

    db = SessionLocal()
    from db.models import Message

    # Kiểm tra đã có thông báo join của user này chưa
    existed = db.query(Message).filter(
        Message.username == "Admin",
        Message.content.like(f"{username} joined at%")
    ).first()

    if not existed:
        msg = Message(username="Admin", content=join_message)
        db.add(msg)
        db.commit()

        # Gửi thông báo join cho tất cả client
        await self.broadcast(websocket, json.dumps({
            "username": "Admin",
            "message": join_message
        }))

    db.close()
  
  async def send_message(self, ws: WebSocket, message: str):
    await ws.send_text(message)

  def find_connection_id(self, websocket: WebSocket):
    websocket_list = list(self.active_connections.values())
    id_list = list(self.active_connections.keys())

    pos = websocket_list.index(websocket)
    return id_list[pos]

  async def broadcast(self, webSocket: WebSocket, data: str):
    decoded_data = json.loads(data)

    for connection in self.active_connections.values():
      is_me = False
      if connection == webSocket:
        is_me = True

      await connection.send_text(json.dumps({"isMe": is_me, "data": decoded_data['message'], "username": decoded_data['username']}))

  def disconnect(self, websocket: WebSocket):
    id = self.find_connection_id(websocket)
    del self.active_connections[id]

    return id

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
connection_manager = ConnectionManager()

app.include_router(auth_router)
app.include_router(chat_router)
