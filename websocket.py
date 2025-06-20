from fastapi import WebSocket, WebSocketDisconnect
from utils import get_ws_user
from db.database import SessionLocal
from db.models import Message
import json

class WSManager:
    def __init__(self):
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    async def broadcast(self, msg: dict):
        for ws in self.active:
            await ws.send_json(msg)

manager = WSManager()

async def websocket_endpoint(websocket: WebSocket):
    db = SessionLocal()

    # Xác thực cookie session của client WebSocket
    try:
        user = await get_ws_user(websocket, db)   # --> trả lỗi & đóng kết nối nếu không hợp lệ
    except RuntimeError:
        db.close()
        return

    await manager.connect(websocket)

    # Gửi 50 tin nhắn lịch sử
    history = (
        db.query(Message)
        .order_by(Message.created_at.desc())
        .limit(50)
        .all()
    )
    for m in reversed(history):
        await websocket.send_json(
            {
                "user": m.user_id,
                "content": m.content,
                "type": m.content_type,
                "lat": m.latitude,
                "lon": m.longitude,
                "ts": m.created_at.isoformat(),
            }
        )

    try:
        while True:
            data = json.loads(await websocket.receive_text())
            msg = Message(
                user_id=user.id,
                content=data["content"],
                content_type=data.get("type", "text"),
                latitude=data.get("lat"),
                longitude=data.get("lon"),
            )
            db.add(msg)
            db.commit()
            db.refresh(msg)

            await manager.broadcast(
                {
                    "user": user.username,
                    "content": msg.content,
                    "type": msg.content_type,
                    "lat": msg.latitude,
                    "lon": msg.longitude,
                    "ts": msg.created_at.isoformat(),
                }
            )
    except WebSocketDisconnect:
        manager.active.remove(websocket)
        db.close()
