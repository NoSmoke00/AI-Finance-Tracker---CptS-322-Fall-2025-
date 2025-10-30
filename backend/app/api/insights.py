from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Dict

from app.database import get_db
from app.auth.router import get_current_user_dependency
from app.models import Insight, User
from app.schemas.insight import InsightResponse
from app.services.insights_service import InsightsAI


router = APIRouter()
ai = InsightsAI()

# naive in-memory rate limit: user_id -> [timestamps]
_GENERATE_CALLS: Dict[int, list] = {}


@router.get("/", response_model=list[InsightResponse])
def list_insights(current_user: User = Depends(get_current_user_dependency), db: Session = Depends(get_db)):
    return ai.get_active_insights(current_user.id, db)


@router.post("/generate", response_model=list[InsightResponse])
def generate_insights(current_user: User = Depends(get_current_user_dependency), db: Session = Depends(get_db)):
    # rate limit 5/hour
    now = datetime.utcnow()
    calls = _GENERATE_CALLS.get(current_user.id, [])
    calls = [t for t in calls if now - t < timedelta(hours=1)]
    if len(calls) >= 5:
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again later.")
    calls.append(now)
    _GENERATE_CALLS[current_user.id] = calls

    return ai.generate_insights_for_user(current_user.id, db)


@router.patch("/{insight_id}/dismiss")
def dismiss_insight(insight_id: int, current_user: User = Depends(get_current_user_dependency), db: Session = Depends(get_db)):
    ins = db.query(Insight).filter(Insight.id == insight_id, Insight.user_id == current_user.id).first()
    if not ins:
        raise HTTPException(status_code=404, detail="Insight not found")
    ins.dismissed = True
    db.commit()
    return {"status": "ok"}


@router.patch("/{insight_id}/view")
def view_insight(insight_id: int, current_user: User = Depends(get_current_user_dependency), db: Session = Depends(get_db)):
    ins = db.query(Insight).filter(Insight.id == insight_id, Insight.user_id == current_user.id).first()
    if not ins:
        raise HTTPException(status_code=404, detail="Insight not found")
    ins.viewed = True
    db.commit()
    return {"status": "ok"}


@router.delete("/{insight_id}")
def delete_insight(insight_id: int, current_user: User = Depends(get_current_user_dependency), db: Session = Depends(get_db)):
    ins = db.query(Insight).filter(Insight.id == insight_id, Insight.user_id == current_user.id).first()
    if not ins:
        raise HTTPException(status_code=404, detail="Insight not found")
    db.delete(ins)
    db.commit()
    return {"status": "ok"}


