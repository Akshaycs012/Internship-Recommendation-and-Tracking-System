from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.db.database import get_db
from app.db import models
from app.api.deps import get_current_user

router = APIRouter(prefix="/applications", tags=["applications"])


# STUDENT APPLIES
@router.post("/apply/{internship_id}")
def apply(internship_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    student = db.query(models.Student).filter_by(user_id=user.id).first()
    if not student:
        raise HTTPException(400, "Student profile missing")

    if not student.resume_url:
        raise HTTPException(400, "Resume required before applying")

    exists = db.query(models.Application).filter_by(
        internship_id=internship_id,
        student_id=student.id
    ).first()
    if exists:
        raise HTTPException(400, "Already applied")

    app = models.Application(
        internship_id=internship_id,
        student_id=student.id,
        status="pending",
        progress_status="pending",
        applied_at=datetime.utcnow(),
        resume_url=student.resume_url
    )

    db.add(app)
    db.add(models.ApplicationLog(
        student_id=student.id,
        internship_id=internship_id,
        event="APPLIED",
        message=f"{student.user.full_name} applied for internship {internship_id}"
    ))

    db.commit()
    return {"message": "Application Submitted"}


# STUDENT CANCEL APPLICATION
@router.delete("/cancel/{internship_id}")
def cancel(internship_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    student = db.query(models.Student).filter_by(user_id=user.id).first()
    app = db.query(models.Application).filter_by(student_id=student.id, internship_id=internship_id).first()

    if not app:
        raise HTTPException(404, "Not applied")

    db.add(models.ApplicationLog(
        student_id=student.id,
        internship_id=internship_id,
        event="CANCELLED",
        message="Student cancelled application"
    ))

    db.delete(app)
    db.commit()
    return {"message": "Application Cancelled"}
