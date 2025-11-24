# backend/app/api/routes/admin.py

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.db.database import get_db
from app.db import models

router = APIRouter(prefix="/admin", tags=["admin"])


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
    admin_user=Depends(require_admin),  # only admins
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


@router.get("/applications")
def list_applications(
    db: Session = Depends(get_db),
    admin_user=Depends(require_admin),  # only admins
):
    apps = db.query(models.Application).all()
    return [
        {
            "id": a.id,
            "student_id": a.student_id,
            "internship_id": a.internship_id,
            "status": a.status,
        }
        for a in apps
    ]
