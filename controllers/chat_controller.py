from fastapi import APIRouter, Request, Depends, Body, Cookie, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, RedirectResponse
from db.models import User, Message
from db.database import get_db, SessionLocal
from authentication.auth import get_current_user
from fastapi.templating import Jinja2Templates
from main import ConnectionManager
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse
from fastapi.exceptions import HTTPException
import json

templates = Jinja2Templates(directory="templates")
router = APIRouter()

@app.websocket("/message")
async def websocket_endpoint(websocket: WebSocket):
    token = websocket.cookies.get("token")
    db = SessionLocal()
    user = db.query(User).filter(User.token == token).first()
    if not user:
        await websocket.close()
        return
    await ConnectionManager.connect(websocket)
    db = SessionLocal()
    # Gửi lại các tin nhắn cũ cho client mới
    old_messages = db.query(Message).order_by(Message.created_at).all()
    for msg in old_messages:
        await ConnectionManager.send_message(
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
                await ConnectionManager.send_message(
                    websocket,
                    json.dumps({"isMe": True, "data": "Username is missing!", "username": "system"})
                )
                continue
            # Lưu tin nhắn vào DB
            msg = Message(username=username, content=message)
            db.add(msg)
            db.commit()
            await ConnectionManager.broadcast(websocket, data)
    except WebSocketDisconnect:
        id = ConnectionManager.disconnect(websocket)
        db.close()
        return RedirectResponse("/")
    
@app.get("/join", response_class=HTMLResponse)
def join_form(request: Request, user: User = Depends(get_current_user)):
    username = user.username
    response = templates.TemplateResponse("index.html", {"request": request, "username": username})
    return response

@app.post("/join")
async def join(request: Request):
    form = await request.form()
    username = form["username"]

    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    db.close()
    response = RedirectResponse("/chat", status_code=302)
    response.set_cookie("username", username)
    if user and user.token:
        response.set_cookie("token", user.token)
    return response

@app.get("/chat", response_class=HTMLResponse)
def chat_room(request: Request, user: User = Depends(get_current_user)):
    username = user.username
    response = templates.TemplateResponse("index.html", {"request": request, "username": username})
    return response
        
@app.post("/api/message")
def create_message(
    data: dict = Body(...),
    token: str = Cookie(None),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.token == token).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    content = data.get("message")
    if not content:
        return {"error": "No message content"}
    msg = Message(username=user.username, content=content)
    db.add(msg)
    db.commit()
    return {"success": True, "message": "Message sent"}
