from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from dataclasses import dataclass
from typing import Dict
import uuid
import json
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from db.database import SessionLocal
from db.models import Message
from sqlalchemy.orm import Session

templates = Jinja2Templates(directory="templates")

@dataclass
class ConnectionManager:
  def __init__(self) -> None:
    self.active_connections: dict = {}

  def get_db():
    print("Opening DB connection")
    db = SessionLocal()
    try:
        yield db
    finally:
        print("Closing DB connection")
        db.close()

  async def connect(self, websocket: WebSocket):
    await websocket.accept()
    id = str(uuid.uuid4())
    self.active_connections[id] = websocket

    await self.send_message(websocket, json.dumps({"isMe": True, "data": "Have joined!!", "username": "You"}))

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

@app.get("/", response_class=HTMLResponse)
def get_room(request: Request):
  return templates.TemplateResponse("index.html", {"request": request});

@app.websocket("/message")
async def websocket_endpoint(websocket: WebSocket):
    await connection_manager.connect(websocket)
    db = SessionLocal()
    # Gửi lại các tin nhắn cũ cho client mới
    old_messages = db.query(Message).order_by(Message.created_at).all()
    for msg in old_messages:
        await connection_manager.send_message(
            websocket,
            json.dumps({"isMe": False, "data": msg.content, "username": msg.username})
        )
    try:
        while True:
            data = await websocket.receive_text()
            decoded = json.loads(data)
            # Lưu tin nhắn vào DB
            msg = Message(username=decoded["username"], content=decoded["message"])
            db.add(msg)
            db.commit()
            await connection_manager.broadcast(websocket, data)
    except WebSocketDisconnect:
        id = connection_manager.disconnect(websocket)
        db.close()
        return RedirectResponse("/")

@app.get("/join", response_class=HTMLResponse)
def get_room(request: Request):
  return templates.TemplateResponse("room.html", {"request": request});

