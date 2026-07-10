from sqlalchemy.orm import Session
from app.repositories.crm import InteractionRepository

def get_dashboard(db: Session, user_id):
    return InteractionRepository(db).metrics(user_id)
