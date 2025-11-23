# backend/app/api/routes/students.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.db import models

router = APIRouter(prefix="/students", tags=["students"])


@router.get("/me/summary")
def get_student_summary(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    # find or create student row
    student = db.query(models.Student).filter(models.Student.user_id == user.id).first()
    if not student:
        student = models.Student(user_id=user.id, skills="")
        db.add(student)
        db.commit()
        db.refresh(student)

    applications = (
        db.query(models.Application)
        .filter(models.Application.student_id == student.id)
        .all()
    )

    total = len(applications)
    accepted = len([a for a in applications if a.status == "selected"])
    pending = len([a for a in applications if a.status == "applied"])

    return {
        "applications": total,
        "accepted": accepted,
        "pending": pending,
        "recent_updates": [
            "Mentor feedback received",
            "Milestone update",
        ],
    }
