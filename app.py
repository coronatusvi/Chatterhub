from fastapi import FastAPI, Depends, HTTPException, Response, status, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from manager import WebSocketManager

# ----- NEW imports -----
from db.schemas import RegisterSchema, LoginSchema
from auth.auth import (
    get_db, hash_pw, verify_pw,
    create_session, get_current_user
)
from sqlalchemy.orm import Session
from db.models import User
# -----------------------

app = FastAPI(title="Chatterhub")

templates = Jinja2Templates(directory="templates")
manager = WebSocketManager()

# ---------- REST AUTH ----------
@app.post("/register", status_code=201)
def register(payload: RegisterSchema, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(400, "Username already exists")
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(400, "Email already exists")
    user = User(
        username=payload.username,
        email=payload.email,
        password_hash=hash_pw(payload.password),
    )
    db.add(user); db.commit(); db.refresh(user)
    token, exp = create_session(db, user.id)
    resp = Response(content="Registered successfully")
    resp.set_cookie("session_token", token, expires=exp, httponly=True, samesite="lax")
    return resp

@app.post("/login")
def login(payload: LoginSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not verify_pw(payload.password, user.password_hash):
        raise HTTPException(401, "Invalid credentials")
    token, exp = create_session(db, user.id)
    resp = Response(content="Login success")
    # nếu remember chọn False ->  session browser
    max_age = 60*60*24*10 if payload.remember else None
    resp.set_cookie("session_token", token, max_age=max_age, expires=exp, httponly=True, samesite="lax")
    return resp

@app.post("/logout")
def logout(resp: Response):
    resp.delete_cookie("session_token")
    resp.body = b"Logged out"
    return resp

# ---------- PAGE ----------
@app.get('/')
async def root(request: Request):
    return templates.TemplateResponse(request, 'index.html', {})

# ---------- WEBSOCKET ----------
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # validate session cookie
    try:
        user = await get_current_user(websocket=websocket)  # modified for WS
    except Exception:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await manager.connect(websocket)

    while True:
        try:
            message = await websocket.receive_json()
            message["client"] = user.username
            for client in manager.connected_clients:
                await manager.send_message(client, message)
        except WebSocketDisconnect:
            await manager.disconnect(websocket)