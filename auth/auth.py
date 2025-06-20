import secrets, hashlib
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, Cookie, status
from sqlalchemy.orm import Session as DBSession
from db.database import SessionLocal
from db.models import User, SessionModel 
from passlib.hash import bcrypt
import websocket

def create_session(db: DBSession, user_id: int):
    token   = secrets.token_hex(32)
    expires = datetime.utcnow() + timedelta(days=SESSION_DAYS)
    sess = SessionModel(user_id=user_id, token=token, expires_at=expires)
    db.add(sess); db.commit()
    return token, expires


# ---------- helper ----------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------- password ----------
def hash_pw(pw: str) -> str:
    return bcrypt.hash(pw)

def verify_pw(pw: str, pw_hash: str) -> bool:
    return bcrypt.verify(pw, pw_hash)

# ---------- session ----------
SESSION_DAYS = 10

def create_session(db: DBSession, user_id: int):
    token   = secrets.token_hex(32)
    expires = datetime.utcnow() + timedelta(days=SESSION_DAYS)
    sess = SessionModel(user_id=user_id, token=token, expires_at=expires)
    db.add(sess); db.commit()
    return token, expires


async def get_current_user(
    session_token: str | None = Cookie(default=None),
    db: DBSession = Depends(get_db)
):
    if not session_token:
        raise HTTPException(401, "Not authenticated")
    sess = db.query(SessionModel).filter(
        SessionModel.token == session_token,
        SessionModel.expires_at >= datetime.utcnow()
    ).first()
    if not sess:
        raise HTTPException(401, "Session expired or invalid")
    return db.query(User).get(sess.user_id)


async def get_ws_user(websocket: websocket, db: DBSession):
    token = websocket.cookies.get("session_token")
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise RuntimeError("No session_token")
    sess = db.query(SessionModel).filter(
        SessionModel.token == token,
        SessionModel.expires_at >= datetime.utcnow()
    ).first()
    if not sess:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise RuntimeError("Invalid or expired session")
    return db.query(User).get(sess.user_id)
