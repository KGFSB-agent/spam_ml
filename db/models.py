from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime
from db.database import Base
from datetime import datetime, timezone

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    balance = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class PredictionHistory(Base):
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    text = Column(String(1000))
    model_type = Column(String(50))
    is_spam = Column(Boolean)
    cost = Column(Float)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
