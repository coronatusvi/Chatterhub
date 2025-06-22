from datetime import datetime

import bcrypt
from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect, Form, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from dataclasses import dataclass
from typing import Dict
import uuid
import json
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from db.database import SessionLocal
from db.models import Message, User
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

    print(f"username", websocket.cookies.get("username"))
    username = websocket.cookies.get("username") or "Unknown"
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

# @app.get("/", response_class=HTMLResponse)
# def get_room(request: Request):
#   return templates.TemplateResponse("index.html", {"request": request})

def get_db():
    print("Opening DB connection")
    db = SessionLocal()
    try:
        yield db
    finally:
        print("Closing DB connection")
        db.close()

@app.get("/", response_class=HTMLResponse)
def login_form(request: Request):
    response = templates.TemplateResponse("login.html", {"request": request})
    response.delete_cookie("username")
    return response

@app.post("/", response_class=HTMLResponse)
def login_or_register(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    email: str = Form(None),
    action: str = Form(...),
    db: Session = Depends(get_db)
):
    if action == "register":
        # Kiểm tra username/email đã tồn tại chưa
        if db.query(User).filter((User.username == username) | (User.email == email)).first():
            return templates.TemplateResponse("login.html", {
                "request": request,
                "error": "Username hoặc email đã tồn tại!",
                "mode": "register"
            })
        # Hash password trước khi lưu
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user = User(username=username, password=hashed_pw, email=email, token="")
        db.add(user)
        db.commit()
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Đăng ký thành công, hãy đăng nhập!",
            "mode": "login"
        })
    else:  # action == "login"
        user = db.query(User).filter(User.username == username).first()
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            response = RedirectResponse(url="/join", status_code=302)
            response.set_cookie(key="username", value=user.username)
            return response
        else:
            return templates.TemplateResponse("login.html", {
                "request": request,
                "error": "Sai tài khoản hoặc mật khẩu",
                "mode": "login"
            })

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
            username = decoded.get("username")
            message = decoded.get("message")
            # Kiểm tra username hợp lệ
            if not username:
                await connection_manager.send_message(
                    websocket,
                    json.dumps({"isMe": True, "data": "Username is missing!", "username": "system"})
                )
                continue
            # Lưu tin nhắn vào DB
            msg = Message(username=username, content=message)
            db.add(msg)
            db.commit()
            await connection_manager.broadcast(websocket, data)
    except WebSocketDisconnect:
        id = connection_manager.disconnect(websocket)
        db.close()
        return RedirectResponse("/")
    
@app.post("/logout")
def logout():
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("username")
    return response

@app.get("/join", response_class=HTMLResponse)
def join_form(request: Request):
    username = request.cookies.get("username")
    response = templates.TemplateResponse("index.html", {"request": request, "username": username})
    # response.headers["Cache-Control"] = "no-store"
    return response

@app.post("/join")
async def join(request: Request):
    form = await request.form()
    username = form["username"]
    response = RedirectResponse("/chat", status_code=302)
    response.set_cookie("username", username)
    return response

@app.get("/chat", response_class=HTMLResponse)
def chat_room(request: Request):
    username = request.cookies.get("username")
    if not username:
        return RedirectResponse("/join")
    response = templates.TemplateResponse("chat.html", {"request": request, "username": username})
    # response.headers["Cache-Control"] = "no-store"
    return response

