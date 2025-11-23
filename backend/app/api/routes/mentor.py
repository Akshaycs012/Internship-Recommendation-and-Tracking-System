from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.db import models

router = APIRouter(prefix="/mentor", tags=["mentor"])


@router.post("/feedback/{application_id}")
def give_feedback(
    application_id: int,
    feedback: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    fb = models.MentorFeedback(
        application_id=application_id,
        mentor_id=user.id,
        feedback_text=feedback
    )
    db.add(fb)
    db.commit()
    return {"message": "Feedback saved"}
