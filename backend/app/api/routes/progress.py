# backend/app/api/routes/progress.py

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.db import models

router = APIRouter(prefix="/progress", tags=["progress"])


@router.get("/milestones")
def get_milestones(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    student = db.query(models.Student).filter(models.Student.user_id == user.id).first()
    if not student:
        return []

    milestones = (
        db.query(models.ProgressMilestone)
        .filter(models.ProgressMilestone.student_id == student.id)
        .all()
    )
    return [
        {
            "id": m.id,
            "title": m.title,
            "is_completed": m.is_completed,
        }
        for m in milestones
    ]


@router.post("/upload")
def upload_deliverable(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    # For demo: We don't store actual file, just acknowledge
    return {"message": f"Received file {file.filename}"}
