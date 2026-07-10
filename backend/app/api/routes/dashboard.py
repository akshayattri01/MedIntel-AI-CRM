from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.services.dashboard import get_dashboard

router = APIRouter()

@router.get("")
def dashboard(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return get_dashboard(db, user.id)
