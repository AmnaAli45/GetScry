from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.db_models import Visitor
from pydantic import BaseModel

router = APIRouter()

# Incoming data ka format define karta hai
class VisitorEvent(BaseModel):
    session_id: str
    total_pages: int
    total_duration: float
    product_pages: int

@router.post("/track")
def track_visitor(event: VisitorEvent, db: Session = Depends(get_db)):
    # Check karein visitor already exist karta hai ya naya hai
    visitor = db.query(Visitor).filter(Visitor.session_id == event.session_id).first()

    if visitor:
        visitor.total_pages = event.total_pages
        visitor.total_duration = event.total_duration
        visitor.product_pages = event.product_pages
    else:
        visitor = Visitor(
            session_id=event.session_id,
            total_pages=event.total_pages,
            total_duration=event.total_duration,
            product_pages=event.product_pages
        )
        db.add(visitor)

    db.commit()
    db.refresh(visitor)

    return {"status": "success", "visitor_id": visitor.id}