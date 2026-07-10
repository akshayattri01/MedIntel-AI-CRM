import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.repositories.crm import HCPRepository
from app.schemas import HCPCreate, HCPRead, HCPUpdate, InteractionRead

router = APIRouter()

@router.get("", response_model=list[HCPRead])
def list_hcps(q: str | None = Query(None), db: Session = Depends(get_db), user=Depends(get_current_user)):
    return HCPRepository(db).list(user.id, q)

@router.post("", response_model=HCPRead)
def create_hcp(payload: HCPCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return HCPRepository(db).create(user.id, payload)

@router.get("/{hcp_id}", response_model=HCPRead)
def get_hcp(hcp_id: uuid.UUID, db: Session = Depends(get_db), user=Depends(get_current_user)):
    hcp = HCPRepository(db).get(user.id, hcp_id)
    if not hcp:
        raise HTTPException(404, "HCP not found")
    return hcp

@router.get("/{hcp_id}/interactions", response_model=list[InteractionRead])
def hcp_history(hcp_id: uuid.UUID, db: Session = Depends(get_db), user=Depends(get_current_user)):
    repo = HCPRepository(db)
    hcp = repo.get(user.id, hcp_id)
    if not hcp:
        raise HTTPException(404, "HCP not found")
    return repo.history(user.id, hcp_id)

@router.patch("/{hcp_id}", response_model=HCPRead)
def update_hcp(hcp_id: uuid.UUID, payload: HCPUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    repo = HCPRepository(db)
    hcp = repo.get(user.id, hcp_id)
    if not hcp:
        raise HTTPException(404, "HCP not found")
    return repo.update(hcp, payload)

@router.delete("/{hcp_id}", status_code=204)
def delete_hcp(hcp_id: uuid.UUID, db: Session = Depends(get_db), user=Depends(get_current_user)):
    repo = HCPRepository(db)
    hcp = repo.get(user.id, hcp_id)
    if not hcp:
        raise HTTPException(404, "HCP not found")
    repo.soft_delete(hcp)
