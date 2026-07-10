from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.schemas import SettingsRead, UserRead, UserUpdate
from app.config import settings

router = APIRouter()

@router.get("/me", response_model=UserRead)
def me(user=Depends(get_current_user)):
    return user

@router.patch("/me", response_model=UserRead)
def update_me(payload: UserUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user

@router.get("/settings", response_model=SettingsRead)
def read_settings(user=Depends(get_current_user)):
    return SettingsRead(user=UserRead.model_validate(user), groq_model=settings.groq_model, api_configured=bool(settings.groq_api_key))
