from database import engine, Base
from models import User, SessionModel, Message

Base.metadata.create_all(bind=engine)