# backend/app/api/routes/students.py

from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.db import models
from app.core.paths import RESUME_DIR

router = APIRouter(prefix="/students", tags=["students"])


def _get_or_create_student(db: Session, user: models.User) -> models.Student:
    student = db.query(models.Student).filter(models.Student.user_id == user.id).first()
    if not student:
        student = models.Student(user_id=user.id, skills="")
        db.add(student)
        db.commit()
        db.refresh(student)
    return student


@router.get("/me/summary")
def get_student_summary(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Dashboard data:
      - applications, accepted, pending counts
      - recent_updates: last ~5 events (task submissions + approvals)
    """
    student = _get_or_create_student(db, user)

    # All applications
    applications = (
        db.query(models.Application)
        .filter(models.Application.student_id == student.id)
        .all()
    )

    total = len(applications)
    accepted = len([a for a in applications if a.status == "approved"])
    pending = len(
        [
            a
            for a in applications
            if a.status in ("applied", "pending")
        ]
    )

    # --------- RECENT UPDATES FEED ---------
    events: list[tuple[datetime, str]] = []

    # Task submissions
    submissions = (
        db.query(models.TaskSubmission)
        .filter(models.TaskSubmission.student_id == student.id)
        .order_by(models.TaskSubmission.submitted_at.desc())
        .limit(5)
        .all()
    )
    for sub in submissions:
        task = (
            db.query(models.InternshipTask)
            .filter(models.InternshipTask.id == sub.task_id)
            .first()
        )
        if not task:
            continue

        label = "On time ✓" if sub.status == "on_time" else "Submitted late ⚠"
        msg = f'Task "{task.title}" submitted — {label}'
        events.append((sub.submitted_at, msg))

    # Application approvals / rejections
    for app in applications:
        internship = app.internship
        if internship is None:
            continue
        # Use id as pseudo-time ordering if created_at is not available
        when = datetime.fromtimestamp(app.id)
        if app.status == "approved":
            msg = f'Your application for "{internship.title}" was approved ✓'
            events.append((when, msg))
        elif app.status == "rejected":
            msg = f'Your application for "{internship.title}" was rejected'
            events.append((when, msg))

    # Sort by timestamp descending and take latest 5
    events.sort(key=lambda x: x[0], reverse=True)
    recent_updates = [msg for _, msg in events[:5]]

    return {
        "applications": total,
        "accepted": accepted,
        "pending": pending,
        "recent_updates": recent_updates,
    }


@router.get("/me/profile")
def get_profile(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Basic profile data for student profile page.
    """
    student = _get_or_create_student(db, user)

    return {
        "name": user.full_name,
        "email": user.email,
        "skills": student.skills or "",
        # Resume URL is not persisted in DB yet
        "resume_url": None,
    }


@router.put("/me/skills")
def update_skills(
    skills: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Update student's skills string.
    Frontend sends as query parameter: /students/me/skills?skills=Python,FastAPI
    """
    student = _get_or_create_student(db, user)
    student.skills = skills
    db.commit()
    return {"message": "Skills updated", "skills": student.skills}


@router.post("/me/resume")
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Save resume file to uploads/resumes.
    We allow all file types.
    """
    student = _get_or_create_student(db, user)

    # Build a safe file name
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    safe_name = f"student_{student.id}_{timestamp}_{file.filename}"
    dest_path = RESUME_DIR / safe_name

    content = await file.read()
    with open(dest_path, "wb") as f:
        f.write(content)

    file_url = f"/uploads/resumes/{safe_name}"

    return {
        "message": "Resume uploaded",
        "file_url": file_url,
    }
