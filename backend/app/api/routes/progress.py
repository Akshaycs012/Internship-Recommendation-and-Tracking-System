# backend/app/api/routes/progress.py

from datetime import date, datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.db import models
from app.core.paths import TASK_FILES_DIR

router = APIRouter(prefix="/progress", tags=["progress"])


def _get_or_create_student(db: Session, user: models.User) -> models.Student:
    student = db.query(models.Student).filter(models.Student.user_id == user.id).first()
    if not student:
        student = models.Student(user_id=user.id, skills="")
        db.add(student)
        db.commit()
        db.refresh(student)
    return student


@router.get("/tasks")
def get_tasks(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Return all tasks for internships where this student has an approved application.
    Each task includes submission status for this student.
    """
    student = _get_or_create_student(db, user)

    approved_apps = (
        db.query(models.Application)
        .filter(
            models.Application.student_id == student.id,
            models.Application.status == "approved",
        )
        .all()
    )

    if not approved_apps:
        return []

    internship_ids = [a.internship_id for a in approved_apps]

    task_rows = (
        db.query(models.InternshipTask, models.Internship)
        .join(models.Internship, models.InternshipTask.internship_id == models.Internship.id)
        .filter(models.InternshipTask.internship_id.in_(internship_ids))
        .order_by(models.InternshipTask.due_date.asc())
        .all()
    )

    today = date.today()
    results = []

    for task, internship in task_rows:
        submission = (
            db.query(models.TaskSubmission)
            .filter(
                models.TaskSubmission.task_id == task.id,
                models.TaskSubmission.student_id == student.id,
            )
            .first()
        )

        if submission:
            status_code = submission.status  # "on_time" or "late"
            submitted_at = submission.submitted_at
            file_url = f"/uploads/tasks/{Path(submission.file_path).name}"
        else:
            status_code = "not_submitted"
            submitted_at = None
            file_url = None

        # derive label for UI
        if status_code == "not_submitted":
            if task.due_date < today:
                label = "Not submitted (Overdue)"
            else:
                label = "Pending"
        elif status_code == "on_time":
            label = "Submitted (On time)"
        else:
            label = "Submitted (Late)"

        results.append(
            {
                "task_id": task.id,
                "internship_title": internship.title,
                "title": task.title,
                "description": task.description,
                "due_date": task.due_date.isoformat(),
                "status": status_code,
                "status_label": label,
                "submitted_at": submitted_at.isoformat() if submitted_at else None,
                "file_url": file_url,
            }
        )

    return results


@router.post("/tasks/{task_id}/submit")
async def submit_task(
    task_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Student uploads a deliverable for a specific task.

    Requirements:
      - Allow ALL file types.
      - Save under uploads/tasks.
      - Status = "on_time" if submitted on or before due_date (by day).
      - Status = "late" if submitted after due_date.
    """
    student = _get_or_create_student(db, user)

    task = db.query(models.InternshipTask).filter(models.InternshipTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Save file to disk
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    safe_name = f"task_{task_id}_student_{student.id}_{timestamp}_{file.filename}"
    dest_path = TASK_FILES_DIR / safe_name

    content = await file.read()
    with open(dest_path, "wb") as f:
        f.write(content)

    # Determine on_time vs late based on calendar day (not hours/seconds)
    today = date.today()
    status_code = "on_time" if today <= task.due_date else "late"

    submission = (
        db.query(models.TaskSubmission)
        .filter(
            models.TaskSubmission.task_id == task_id,
            models.TaskSubmission.student_id == student.id,
        )
        .first()
    )

    now = datetime.now(timezone.utc)

    if submission:
        submission.file_path = str(dest_path)
        submission.submitted_at = now
        submission.status = status_code
    else:
        submission = models.TaskSubmission(
            task_id=task_id,
            student_id=student.id,
            file_path=str(dest_path),
            submitted_at=now,
            status=status_code,
        )
        db.add(submission)

    db.commit()
    db.refresh(submission)

    return {
        "message": "Task submitted",
        "status": submission.status,
        "file_url": f"/uploads/tasks/{dest_path.name}",
    }
