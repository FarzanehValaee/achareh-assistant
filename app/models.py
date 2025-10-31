from sqlalchemy import Column, Integer, String, DateTime
from app.db import Base
from datetime import datetime

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    message = Column(String)
    response = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)