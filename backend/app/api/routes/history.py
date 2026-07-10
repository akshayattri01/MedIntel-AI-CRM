from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models import InteractionHistory
from app.serialization import json_safe

router = APIRouter()

@router.get("")
def history(db: Session = Depends(get_db), user=Depends(get_current_user)):
    rows = db.scalars(select(InteractionHistory).where(InteractionHistory.actor_id == user.id).order_by(InteractionHistory.created_at.desc()).limit(50)).all()
    return json_safe([{"id": str(r.id), "event_type": r.event_type, "payload": r.payload, "created_at": r.created_at} for r in rows])
