# backend/app/api/routes/mentor.py

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import require_mentor
from app.db.database import get_db
from app.db import models

router = APIRouter(prefix="/mentor", tags=["mentor"])


class FeedbackCreate(BaseModel):
    student_id: int
    feedback_text: str


@router.get("/me")
def get_mentor_profile(
    mentor_user=Depends(require_mentor),
):
    return {
        "id": mentor_user.id,
        "email": mentor_user.email,
        "full_name": mentor_user.full_name,
        "role": mentor_user.role,
    }


@router.get("/students")
def list_students_for_mentor(
    db: Session = Depends(get_db),
    mentor_user=Depends(require_mentor),
):
    # For now: return all students (you can later filter by mentor)
    students = db.query(models.Student).all()
    return [
        {
            "id": s.id,
            "user_id": s.user_id,
        }
        for s in students
    ]


@router.post("/feedback")
def give_feedback(
    payload: FeedbackCreate,
    db: Session = Depends(get_db),
    mentor_user=Depends(require_mentor),
):
    fb = models.MentorFeedback(
        student_id=payload.student_id,
        mentor_user_id=mentor_user.id,
        feedback_text=payload.feedback_text,
    )
    db.add(fb)
    db.commit()
    db.refresh(fb)
    return {"id": fb.id, "message": "Feedback saved"}
