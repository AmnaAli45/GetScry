from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.db_models import Visitor
import json

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def get_tier(score: float) -> str:
    if score is None:
        return "unknown"
    if score >= 70:
        return "high"
    elif score >= 30:
        return "medium"
    return "low"


@router.get("/dashboard")
def dashboard(request: Request, db: Session = Depends(get_db)):
    visitors = db.query(Visitor).order_by(Visitor.intent_score.desc()).all()

    visitor_rows = []
    for v in visitors:
        score = v.intent_score if v.intent_score is not None else 0
        reasons = json.loads(v.reasons) if v.reasons else []
        visitor_rows.append({
            "id": v.id,
            "session_id": v.session_id,
            "total_pages": v.total_pages,
            "total_duration": round(v.total_duration, 1) if v.total_duration else 0,
            "product_pages": v.product_pages,
            "intent_score": round(score, 1),
            "tier": get_tier(score),
            "reasons": reasons,
            "created_at": v.created_at.strftime("%b %d, %H:%M") if v.created_at else "",
        })

    total_visitors = len(visitor_rows)
    high_count = sum(1 for v in visitor_rows if v["tier"] == "high")
    medium_count = sum(1 for v in visitor_rows if v["tier"] == "medium")
    low_count = sum(1 for v in visitor_rows if v["tier"] == "low")
    avg_score = round(sum(v["intent_score"] for v in visitor_rows) / total_visitors, 1) if total_visitors else 0

    # Line chart ke liye: score trend, sabse purane se naye order mein (chronological)
    chronological = sorted(visitor_rows, key=lambda x: x["id"])
    trend_labels = [v["session_id"][:8] for v in chronological][-12:]
    trend_scores = [v["intent_score"] for v in chronological][-12:]

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "visitors": visitor_rows,
        "total_visitors": total_visitors,
        "high_intent_count": high_count,
        "medium_intent_count": medium_count,
        "low_intent_count": low_count,
        "avg_score": avg_score,
        "trend_labels": json.dumps(trend_labels),
        "trend_scores": json.dumps(trend_scores),
    })