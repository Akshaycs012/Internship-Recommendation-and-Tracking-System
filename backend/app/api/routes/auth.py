from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import timedelta

from app.db.database import get_db
from app.db import models
from app.core.security import create_access_token, verify_password, get_password_hash
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])


class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    role: str  # student, mentor, admin


class UserLogin(BaseModel):
    email: str
    password: str


@router.post("/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email exists")

    new_user = models.User(
        email=user.email,
        hashed_password=get_password_hash(user.password),
        full_name=user.full_name,
        role=user.role,
    )
    db.add(new_user)
    db.commit()

    token = create_access_token({"sub": str(new_user.id), "role": new_user.role})
    return {"access_token": token, "token_type": "bearer"}


@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(
        {"sub": str(db_user.id), "role": db_user.role},
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": token, "token_type": "bearer"}
