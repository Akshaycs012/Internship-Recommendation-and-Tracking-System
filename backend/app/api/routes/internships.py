from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db import models

router = APIRouter(prefix="/internships", tags=["internships"])


@router.get("/recommendations")
def get_recommendations(
    keywords: str = "",
    skills: str = "",
    db: Session = Depends(get_db),
):
    internships = db.query(models.Internship).all()

    # simple score based on keyword/skills match
    results = []
    for i in internships:
        score = 0
        if keywords.lower() in i.title.lower():
            score += 30
        if skills.lower() in (i.required_skills or "").lower():
            score += 50

        results.append({
            "id": i.id,
            "title": i.title,
            "company": i.company,
            "skills": i.required_skills,
            "match": score
        })

    results.sort(key=lambda x: x["match"], reverse=True)
    return results
