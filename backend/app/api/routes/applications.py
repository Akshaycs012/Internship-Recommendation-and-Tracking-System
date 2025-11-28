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


# ========== ADMIN — APPROVE / REJECT APPLICATION ==========
@router.post("/update-status/{app_id}")
def update_application_status(app_id: int, status: str,
                              db: Session = Depends(get_db),
                              admin=Depends(get_current_user)):

    if admin.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")

    app = db.query(models.Application).filter(models.Application.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    if status not in ["approved", "rejected"]:
        raise HTTPException(status_code=400, detail="Invalid status")

    app.status = status
    db.commit()

    return {"message": "Status updated", "status": status}
