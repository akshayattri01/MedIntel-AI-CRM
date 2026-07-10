import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.repositories.crm import InteractionRepository
from app.schemas import InteractionCreate, InteractionRead, InteractionUpdate

router = APIRouter()

@router.get("", response_model=list[InteractionRead])
def list_interactions(q: str | None = Query(None), sentiment: str | None = None, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return InteractionRepository(db).list(user.id, q=q, sentiment=sentiment)

@router.post("", response_model=InteractionRead)
def create_interaction(payload: InteractionCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    try:
        return InteractionRepository(db).create(user.id, payload)
    except ValueError as exc:
        raise HTTPException(400, str(exc))

@router.get("/{interaction_id}", response_model=InteractionRead)
def get_interaction(interaction_id: uuid.UUID, db: Session = Depends(get_db), user=Depends(get_current_user)):
    item = InteractionRepository(db).get(user.id, interaction_id)
    if not item:
        raise HTTPException(404, "Interaction not found")
    return item

@router.patch("/{interaction_id}", response_model=InteractionRead)
def update_interaction(interaction_id: uuid.UUID, payload: InteractionUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    repo = InteractionRepository(db)
    item = repo.get(user.id, interaction_id)
    if not item:
        raise HTTPException(404, "Interaction not found")
    return repo.update(item, user.id, payload)

@router.delete("/{interaction_id}", status_code=204)
def delete_interaction(interaction_id: uuid.UUID, db: Session = Depends(get_db), user=Depends(get_current_user)):
    repo = InteractionRepository(db)
    item = repo.get(user.id, interaction_id)
    if not item:
        raise HTTPException(404, "Interaction not found")
    repo.soft_delete(item, user.id)
