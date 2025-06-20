from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from ..database import get_db
from ..db.models import User
from ..auth.auth import hash_pw, create_session

router = APIRouter(prefix="/auth")

class RegisterSchema(BaseModel):
    username: str
    email: EmailStr
    password: str

@router.post("/register")
def register(payload: RegisterSchema, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(400, "Username exists")
    user = User(
        username=payload.username,
        email=payload.email,
        password_hash=hash_pw(payload.password)
    )
    db.add(user); db.commit(); db.refresh(user)
    token, exp = create_session(db, user.id)
    resp = Response(content="Registered")
    resp.set_cookie("session_token", token, expires=exp, httponly=True)
    return resp
