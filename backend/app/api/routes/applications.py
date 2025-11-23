from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db import models
from app.api.deps import get_current_user

router = APIRouter(prefix="/applications", tags=["applications"])


@router.post("/apply/{internship_id}")
def apply(internship_id: int,
          db: Session = Depends(get_db),
          user=Depends(get_current_user)):

    student = db.query(models.Student).filter(models.Student.user_id == user.id).first()

    app = models.Application(
        student_id=student.id,
        internship_id=internship_id,
        status="applied"
    )

    db.add(app)
    db.commit()
    return {"message": "Application submitted"}
