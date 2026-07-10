from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.services.dashboard import get_dashboard

router = APIRouter()

@router.get("")
def analytics(db: Session = Depends(get_db), user=Depends(get_current_user)):
    data = get_dashboard(db, user.id)
    return {
        "meetings": data["monthly_interactions"],
        "sentiment": data.get("sentiment_breakdown", []),
        "products": data.get("product_discussions", []),
        "follow_up_completion": data.get("follow_up_completion", 0),
    }
