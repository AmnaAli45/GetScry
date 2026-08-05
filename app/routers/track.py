from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.db_models import Visitor
from app.ml.predict import predict_purchase
from pydantic import BaseModel
from datetime import datetime
import json

router = APIRouter()

MONTH_MAP = {
    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "June",
    7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"
}


class VisitorEvent(BaseModel):
    session_id: str
    total_pages: int
    total_duration: float
    product_pages: int
    administrative: int = 0
    administrative_duration: float = 0.0
    informational: int = 0
    informational_duration: float = 0.0
    bounce_rates: float = 0.0
    exit_rates: float = 0.0
    page_values: float = 0.0
    special_day: float = 0.0
    operating_systems: int = 2
    browser: int = 2
    region: int = 1
    traffic_type: int = 2


@router.post("/track")
def track_visitor(event: VisitorEvent, db: Session = Depends(get_db)):
    visitor = db.query(Visitor).filter(Visitor.session_id == event.session_id).first()
    visitor_type = "Returning_Visitor" if visitor else "New_Visitor"

    now = datetime.now()
    month = MONTH_MAP[now.month]
    weekend = now.weekday() >= 5

    result = predict_purchase(
        administrative=event.administrative,
        administrative_duration=event.administrative_duration,
        informational=event.informational,
        informational_duration=event.informational_duration,
        product_pages=event.product_pages,
        product_duration=event.total_duration,
        bounce_rates=event.bounce_rates,
        exit_rates=event.exit_rates,
        page_values=event.page_values,
        special_day=event.special_day,
        operating_systems=event.operating_systems,
        browser=event.browser,
        region=event.region,
        traffic_type=event.traffic_type,
        weekend=weekend,
        month=month,
        visitor_type=visitor_type,
    )

    reasons_json = json.dumps(result["reasons"])

    if visitor:
        visitor.total_pages = event.total_pages
        visitor.total_duration = event.total_duration
        visitor.product_pages = event.product_pages
        visitor.intent_score = result["intent_score"]
        visitor.reasons = reasons_json
    else:
        visitor = Visitor(
            session_id=event.session_id,
            total_pages=event.total_pages,
            total_duration=event.total_duration,
            product_pages=event.product_pages,
            intent_score=result["intent_score"],
            reasons=reasons_json
        )
        db.add(visitor)

    db.commit()
    db.refresh(visitor)

    return {
        "status": "success",
        "visitor_id": visitor.id,
        "intent_score": result["intent_score"],
        "reasons": result["reasons"]
    }