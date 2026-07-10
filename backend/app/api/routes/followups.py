import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.repositories.crm import FollowUpRepository
from app.schemas import FollowUpRead

router = APIRouter()

@router.get("", response_model=list[FollowUpRead])
def list_followups(status: str | None = None, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return FollowUpRepository(db).list(user.id, status)

@router.patch("/{follow_up_id}/complete", response_model=FollowUpRead)
def complete_followup(follow_up_id: uuid.UUID, db: Session = Depends(get_db), user=Depends(get_current_user)):
    item = FollowUpRepository(db).complete(user.id, follow_up_id)
    if not item:
        raise HTTPException(404, "Follow-up not found")
    return item
