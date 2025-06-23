from db.database import get_db
from db.models import User
from fastapi import Cookie, HTTPException, Depends
from sqlalchemy.orm import Session

def get_current_user(token: str = Cookie(None), db: Session = Depends(get_db)):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user = db.query(User).filter(User.token == token).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user