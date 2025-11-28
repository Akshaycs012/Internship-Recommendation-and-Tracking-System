# backend/app/api/routes/admin.py

from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.db.database import get_db
from app.db import models

router = APIRouter(prefix="/admin", tags=["admin"])


# ---------------- CREATE INTERNSHIP ----------------
class InternshipCreate(BaseModel):
    title: str
    company: str
    location: str | None = None
    skills: str | None = None
    industry: str | None = None


@router.post("/internships")
def add_internship(
    data: InternshipCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    internship = models.Internship(
        title=data.title,
        company=data.company,
        location=data.location or "",
        required_skills=data.skills or "",
        industry=data.industry or "",
    )
    db.add(internship)
    db.commit()
    db.refresh(internship)
    return {"id": internship.id, "message": "Internship added"}


@router.get("/internships")
def list_internships(
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    return db.query(models.Internship).all()


# ---------------- TASK CREATION FOR INTERNSHIPS ----------------

class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    due_date: date


@router.post("/internships/{internship_id}/tasks")
def create_task_for_internship(
    internship_id: int,
    payload: TaskCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    internship = (
        db.query(models.Internship)
        .filter(models.Internship.id == internship_id)
        .first()
    )
    if not internship:
        raise HTTPException(status_code=404, detail="Internship not found")

    # simple ordering by count
    existing_count = (
        db.query(models.InternshipTask)
        .filter(models.InternshipTask.internship_id == internship_id)
        .count()
    )

    task = models.InternshipTask(
        internship_id=internship_id,
        title=payload.title,
        description=payload.description or "",
        due_date=payload.due_date,
        order_index=existing_count + 1,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return {"id": task.id, "message": "Task created"}


@router.get("/internships/{internship_id}/tasks")
def list_tasks_for_internship(
    internship_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    tasks = (
        db.query(models.InternshipTask)
        .filter(models.InternshipTask.internship_id == internship_id)
        .order_by(models.InternshipTask.due_date.asc())
        .all()
    )
    return [
        {
            "id": t.id,
            "title": t.title,
            "description": t.description,
            "due_date": t.due_date.isoformat(),
        }
        for t in tasks
    ]


@router.post("/internships/create")
def create_internship(data: dict, db: Session = Depends(get_db), admin=Depends(require_admin)):

    internship = models.Internship(
        title=data["title"],
        company=data["company"],
        location=data.get("location",""),
        required_skills=data.get("required_skills",""),
        industry=data.get("industry","")
    )

    db.add(internship)
    db.commit()
    db.refresh(internship)
    return {"message":"Internship created", "id":internship.id}


# ========== APPLICANTS FETCH FOR ADMIN PANEL ==========
@router.get("/internships/{internship_id}/applications")
def admin_get_applications(internship_id: int, status: str | None = None,
                           db: Session = Depends(get_db),
                           admin=Depends(require_admin)):

    q = db.query(models.Application).filter(models.Application.internship_id == internship_id)

    if status in ["pending", "approved", "rejected"]:
        q = q.filter(models.Application.status == status)

    apps = q.all()

    return [
        {
            "id": a.id,
            "student": db.query(models.User).filter(models.User.id == a.student.user_id).first().full_name,
            "email": db.query(models.User).filter(models.User.id == a.student.user_id).first().email,
            "internship": a.internship.title,
            "status": a.status
        }
        for a in apps
    ]


# ================= APPLICATION MANAGEMENT ================= #

@router.get("/applications")
def admin_get_applications(db: Session = Depends(get_db), admin=Depends(require_admin)):
    apps = (
        db.query(models.Application, models.User, models.Internship)
        .join(models.Student, models.Application.student_id == models.Student.id)
        .join(models.User, models.Student.user_id == models.User.id)
        .join(models.Internship, models.Application.internship_id == models.Internship.id)
        .all()
    )

    return [
        {
            "id": a.Application.id,
            "student_name": a.User.full_name,
            "internship_title": a.Internship.title,
            "status": a.Application.status,
        }
        for a in apps
    ]


@router.patch("/applications/{app_id}/approve")
def approve_application(
    app_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    app = db.query(models.Application).filter(models.Application.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    app.status = "approved"
    db.commit()
    return {"message": "Application approved"}


@router.patch("/applications/{app_id}/reject")
def reject_application(
    app_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    app = db.query(models.Application).filter(models.Application.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    app.status = "rejected"
    db.commit()
    return {"message": "Application rejected"}
