from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from .database import Base

class User(Base):
    __tablename__ = "users"
    id          = Column(Integer, primary_key=True, index=True)
    username    = Column(String, unique=True, nullable=False)
    email       = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at  = Column(DateTime, default=datetime.utcnow)

class SessionModel(Base):
    __tablename__ = "sessions"
    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"))
    token      = Column(String, unique=True, index=True)
    expires_at = Column(DateTime)

class Message(Base):
    __tablename__ = "messages"
    id           = Column(Integer, primary_key=True, index=True)
    user_id      = Column(Integer, ForeignKey("users.id"))
    content      = Column(Text)
    content_type = Column(String, default="text")       # text | location | emoji
    latitude     = Column(Float)
    longitude    = Column(Float)
    created_at   = Column(DateTime, default=datetime.utcnow)
