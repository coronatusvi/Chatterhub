from datetime import datetime
from fastapi import status
from db.models import SessionModel, User
import websocket
from sqlalchemy.orm import Session as DBSession


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
