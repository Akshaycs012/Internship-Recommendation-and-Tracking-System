from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.db import models

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/internships")
def add_internship(
    title: str,
    company: str,
    location: str = "",
    skills: str = "",
    industry: str = "",
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    internship = models.Internship(
        title=title,
        company=company,
        location=location,
        required_skills=skills,
        industry=industry,
    )
    db.add(internship)
    db.commit()

    return {"message": "Internship added"}
