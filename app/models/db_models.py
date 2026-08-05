from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from datetime import datetime
from app.database import Base

class Visitor(Base):
    __tablename__ = "visitors"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    total_pages = Column(Integer, default=0)
    total_duration = Column(Float, default=0.0)
    product_pages = Column(Integer, default=0)
    intent_score = Column(Float, nullable=True)
    reasons = Column(Text, nullable=True)   # naya column - top reasons ko comma-separated / JSON string mein save karega
    created_at = Column(DateTime, default=datetime.utcnow)