from app.models import Message
from app.database import SessionLocal

def test_store_message():
    db = SessionLocal()
    msg = Message(user_id=1, content="hello")
    db.add(msg); db.commit(); db.refresh(msg)
    assert msg.id > 0
    db.delete(msg); db.commit()
