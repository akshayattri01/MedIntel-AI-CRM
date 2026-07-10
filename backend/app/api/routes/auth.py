from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.auth.security import create_access_token, create_refresh_token, hash_password, verify_password
from app.database import get_db
from app.models import RefreshToken, User
from app.schemas import LoginRequest, RefreshRequest, Token, UserCreate, UserRead

router = APIRouter()

def issue_tokens(db: Session, user: User) -> Token:
    refresh_token, expires_at = create_refresh_token()
    db.add(RefreshToken(user_id=user.id, token=refresh_token, expires_at=expires_at))
    db.commit()
    return Token(access_token=create_access_token(str(user.id)), refresh_token=refresh_token, user=UserRead.model_validate(user))

@router.post("/register", response_model=Token)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    if db.scalar(select(User).where(User.email == payload.email)):
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(email=payload.email, full_name=payload.full_name, hashed_password=hash_password(payload.password))
    db.add(user)
    db.flush()
    db.refresh(user)
    return issue_tokens(db, user)

@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == payload.email, User.is_deleted.is_(False)))
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return issue_tokens(db, user)

@router.post("/refresh", response_model=Token)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    token = db.scalar(
        select(RefreshToken)
        .where(RefreshToken.token == payload.refresh_token, RefreshToken.revoked_at.is_(None), RefreshToken.is_deleted.is_(False))
    )
    if not token or token.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    token.revoked_at = datetime.now(timezone.utc)
    user = db.get(User, token.user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not active")
    return issue_tokens(db, user)

@router.post("/logout", status_code=204)
def logout(payload: RefreshRequest, db: Session = Depends(get_db)):
    token = db.scalar(select(RefreshToken).where(RefreshToken.token == payload.refresh_token, RefreshToken.revoked_at.is_(None)))
    if token:
        token.revoked_at = datetime.now(timezone.utc)
        db.commit()

@router.post("/forgot-password")
def forgot_password():
    return {"message": "If an account exists, a reset workflow will be sent."}
