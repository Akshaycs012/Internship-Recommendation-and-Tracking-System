# backend/app/api/routes/applications.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.db import models

router = APIRouter(prefix="/applications", tags=["applications"])


@router.post("/apply/{internship_id}")
def apply_to_internship(
    internship_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    internship = (
        db.query(models.Internship).filter(models.Internship.id == internship_id).first()
    )
    if not internship:
        raise HTTPException(status_code=404, detail="Internship not found")

    student = db.query(models.Student).filter(models.Student.user_id == user.id).first()
    if not student:
        student = models.Student(user_id=user.id, skills="")
        db.add(student)
        db.commit()
        db.refresh(student)

    existing = (
        db.query(models.Application)
        .filter(
            models.Application.student_id == student.id,
            models.Application.internship_id == internship.id,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Already applied")

    app_obj = models.Application(
        student_id=student.id,
        internship_id=internship.id,
        status="applied",
    )
    db.add(app_obj)
    db.commit()
    return {"message": "Application submitted"}
