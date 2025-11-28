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
def add_internship(data: InternshipCreate, db: Session = Depends(get_db), admin=Depends(require_admin)):
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
def list_internships(db: Session = Depends(get_db), admin=Depends(require_admin)):
    return db.query(models.Internship).all()



# =================== APPLICATIONS - LIST FOR ADMIN PANEL ===================

@router.get("/applications")
def admin_all_applications(db: Session = Depends(get_db), admin=Depends(require_admin)):

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
def admin_internship_applications(intern_id:int, status:str|None=None,
                                  db:Session=Depends(get_db), admin=Depends(require_admin)):

    q = db.query(models.Application)\
          .filter(models.Application.internship_id==intern_id)

    if status in ("pending","approved","rejected"):
        q = q.filter(models.Application.status==status)

    result=[]
    for a in q.all():
        student=db.query(models.User).join(models.Student)\
                .filter(models.Student.id==a.student_id).first()
        result.append({
            "id": a.id,
            "student": student.full_name,
            "email": student.email,
            "status": a.status
        })

    return result


# =================== APPROVE & REJECT ===================

@router.patch("/applications/{app_id}/approve")
def approve(app_id:int, db:Session=Depends(get_db), admin=Depends(require_admin)):
    app=db.query(models.Application).filter_by(id=app_id).first()
    if not app: raise HTTPException(404,"Not found")
    app.status="approved"; db.commit()
    return {"message":"Approved"}

@router.patch("/applications/{app_id}/reject")
def reject(app_id:int, db:Session=Depends(get_db), admin=Depends(require_admin)):
    app=db.query(models.Application).filter_by(id=app_id).first()
    if not app: raise HTTPException(404,"Not found")
    app.status="rejected"; db.commit()
    return {"message":"Rejected"}
