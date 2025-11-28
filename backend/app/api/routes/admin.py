from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.db.database import get_db
from app.db import models

router = APIRouter(prefix="/admin", tags=["admin"])


# =================== CREATE INTERNSHIP ===================

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
    return {"message": "Internship created", "id": internship.id}


@router.get("/internships")
def list_internships(
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    return db.query(models.Internship).all()


# =================== APPLICATIONS - LIST FOR ADMIN PANEL ===================

@router.get("/applications")
def admin_all_applications(
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
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


# =================== APPLICATIONS - FILTER VIEW PAGE ===================

@router.get("/internships/{intern_id}/applications")
def admin_internship_applications(
    intern_id: int,
    status: str | None = None,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """
    Applications for a specific internship (used by admin-internships page).
    Now also returns resume_url so admin can open the PDF in browser.
    """
    q = (
        db.query(models.Application)
        .filter(models.Application.internship_id == intern_id)
    )

    if status in ("pending", "approved", "rejected"):
        q = q.filter(models.Application.status == status)

    result = []
    for a in q.all():
        student_obj = db.query(models.Student).filter_by(id=a.student_id).first()
        if not student_obj:
            # should not happen, but skip invalid records instead of crashing UI
            continue
        user = student_obj.user

        result.append(
            {
                "id": a.id,
                "student": user.full_name,
                "email": user.email,
                "status": a.status,
                # NEW: url for View Resume button
                "resume_url": student_obj.resume_path,
            }
        )

    return result


# =================== APPROVE & REJECT ===================

@router.patch("/applications/{app_id}/approve")
def approve(
    app_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    app = db.query(models.Application).filter_by(id=app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Not found")
    app.status = "approved"
    db.commit()
    return {"message": "Approved"}


@router.patch("/applications/{app_id}/reject")
def reject(
    app_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    app = db.query(models.Application).filter_by(id=app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Not found")
    app.status = "rejected"
    db.commit()
    return {"message": "Rejected"}


@router.get("/internships/{internship_id}/applicants")
def get_internship_applicants(internship_id: int, db: Session = Depends(get_db), admin=Depends(require_admin)):

    apps = (
        db.query(models.Application, models.User, models.Student)
        .join(models.Student, models.Application.student_id == models.Student.id)
        .join(models.User, models.Student.user_id == models.User.id)
        .filter(models.Application.internship_id == internship_id)
        .all()
    )

    return [
        {
            "application_id": a.Application.id,
            "name": a.User.full_name,
            "email": a.User.email,
            "resume": None,  # later we add upload
            "status": a.Application.status,
        }
        for a in apps
    ]


# =================== VIEW APPLICANTS FOR SPECIFIC INTERNSHIP ===================

@router.get("/internships/{intern_id}/applicants")
def view_applicants(intern_id: int, db: Session = Depends(get_db), admin=Depends(require_admin)):
    """
    Returns list of all applicants for a specific internship.
    Includes: student name, email, resume, status, application_id
    """

    data = (
        db.query(models.Application, models.User, models.Student)
        .join(models.Student, models.Application.student_id == models.Student.id)
        .join(models.User, models.Student.user_id == models.User.id)
        .filter(models.Application.internship_id == intern_id)
        .all()
    )

    if not data:
        return []

    result = []
    for a, user, student in data:
        result.append({
            "application_id": a.id,
            "name": user.full_name,
            "email": user.email,
            "resume": None,  # will replace later when resume upload endpoint added
            "status": a.status,
        })

    return result


# =================== APPROVE / REJECT FROM APPLICANT TABLE ===================

@router.patch("/applications/{application_id}/approve")
def approve_applicant(application_id: int, db: Session = Depends(get_db), admin=Depends(require_admin)):
    app = db.query(models.Application).filter_by(id=application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    app.status = "approved"
    db.commit()
    return {"message": "Student Approved"}


@router.patch("/applications/{application_id}/reject")
def reject_applicant(application_id: int, db: Session = Depends(get_db), admin=Depends(require_admin)):
    app = db.query(models.Application).filter_by(id=application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    app.status = "rejected"
    db.commit()
    return {"message": "Student Rejected"}
