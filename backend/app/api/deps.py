# backend/app/api/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.db.database import get_db
from app.db import models
from app.core.config import settings


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ---------------------- Get Current User (Core Auth) ---------------------- #
def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        # Decode using the same key/algorithm as used for token creation
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        user_id: int | None = payload.get("sub")

        if not user_id:
            raise JWTError()

        user = db.query(models.User).filter(models.User.id == int(user_id)).first()
        if not user:
            raise JWTError()

        return user

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
        )


# ---------------------- Student Only Access ---------------------- #
def get_current_student(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Students only")

    student = db.query(models.Student).filter(models.Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile missing")

    return student


# ---------------------- Admin Only Access ---------------------- #
def require_admin(current_user: models.User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    return current_user


# ---------------------- Mentor Only Access ---------------------- #
def require_mentor(current_user: models.User = Depends(get_current_user)):
    if current_user.role != "mentor":
        raise HTTPException(status_code=403, detail="Mentors only")
    return current_user
