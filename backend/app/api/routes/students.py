from datetime import datetime, date
from pathlib import Path

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.db import models
from app.core.paths import RESUME_DIR

router = APIRouter(prefix="/students", tags=["students"])


# ========================================================
# INTERNAL — ENSURE STUDENT PROFILE EXISTS
# ========================================================
def _get_or_create_student(db: Session, user: models.User) -> models.Student:
    student = db.query(models.Student).filter_by(user_id=user.id).first()
    if not student:
        student = models.Student(user_id=user.id, skills="")
        db.add(student)
        db.commit()
        db.refresh(student)
    return student


# ========================================================
# PROFILE STRUCTURE
# ========================================================
class StudentProfileUpdate(BaseModel):
    full_name: str | None = None
    skills: str | None = None
    age: int | None = None
    date_of_birth: date | None = None
    phone: str | None = None
    education: str | None = None
    experience: str | None = None
    linkedin_url: str | None = None
    github_url: str | None = None
    portfolio_url: str | None = None
    skills_rating: str | None = None


# ========================================================
# GET PROFILE — frontend uses this to load page
# ========================================================
@router.get("/me/profile")
def get_profile(db: Session = Depends(get_db), user=Depends(get_current_user)):
    student = _get_or_create_student(db, user)

    profile_complete = bool(student.phone and student.education and student.resume_url)

    return {
        "name": user.full_name,
        "email": user.email,
        "skills": student.skills or "",
        "age": student.age,
        "date_of_birth": student.date_of_birth.isoformat() if student.date_of_birth else None,
        "phone": student.phone,
        "education": student.education,
        "experience": student.experience,
        "linkedin_url": student.linkedin_url,
        "github_url": student.github_url,
        "portfolio_url": student.portfolio_url,
        "skills_rating": student.skills_rating,
        "resume_url": student.resume_url,
        "profile_complete": profile_complete
    }


# ========================================================
# UPDATE FULL PROFILE (Save + Modify)
# ========================================================
@router.put("/me/profile")
def update_profile(payload: StudentProfileUpdate,
                   db: Session = Depends(get_db),
                   user=Depends(get_current_user)):

    student = _get_or_create_student(db, user)

    # user
    if payload.full_name is not None:
        user.full_name = payload.full_name

    # student fields
    for field, value in payload.dict(exclude_unset=True).items():
        if hasattr(student, field):
            setattr(student, field, value)

    db.commit()
    return get_profile(db, user)


# ========================================================
# UPLOAD RESUME + save file path in DB
# ========================================================
@router.post("/me/resume")
async def upload_resume(file: UploadFile = File(...),
                        db: Session = Depends(get_db),
                        user=Depends(get_current_user)):

    student = _get_or_create_student(db, user)

    RESUME_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    filename = f"resume_{student.id}_{timestamp}_{file.filename}"
    path = RESUME_DIR / filename

    with open(path, "wb") as f:
        f.write(await file.read())

    student.resume_url = f"/uploads/resumes/{filename}"
    db.commit()

    return {"message": "Resume Uploaded", "resume_url": student.resume_url}

