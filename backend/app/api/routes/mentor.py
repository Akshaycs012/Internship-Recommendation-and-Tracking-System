# backend/app/api/routes/mentor.py

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.db import models

router = APIRouter(prefix="/mentor", tags=["mentor"])


class FeedbackCreate(BaseModel):
    student_id: int
    feedback_text: str


@router.get("/students")
def list_students_for_mentor(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    # Simple: return all students
    students = db.query(models.Student).all()
    return [{"id": s.id, "user_id": s.user_id} for s in students]


@router.post("/feedback")
def give_feedback(
    payload: FeedbackCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    fb = models.MentorFeedback(
        student_id=payload.student_id,
        mentor_user_id=user.id,
        feedback_text=payload.feedback_text,
    )
    db.add(fb)
    db.commit()
    return {"message": "Feedback saved"}
