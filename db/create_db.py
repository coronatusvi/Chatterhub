# --- Nội dung từ database.py ---
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./chat.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Nội dung từ models.py ---
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    content = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)                          

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    email = Column(String, unique=True, index=True)
    token = Column(String)

# --- Nội dung từ create.py ---
# Phần này phải được đặt SAU khi Base và các model đã được định nghĩa.
Base.metadata.create_all(bind=engine)

# Bạn có thể thêm một số mã để kiểm tra xem mọi thứ đã tạo thành công chưa
print("Database tables created successfully or already exist.")