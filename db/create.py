from database import Base, engine
from models import Message

Base.metadata.create_all(bind=engine)       