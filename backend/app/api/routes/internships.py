# backend/app/api/routes/internships.py

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db import models
from app.api.deps import get_current_user

router = APIRouter(prefix="/internships", tags=["internships"])


def _normalize_skills(skills_str: str | None) -> set[str]:
    if not skills_str:
        return set()
    return {s.strip().lower() for s in skills_str.split(",") if s.strip()}


@router.get("/recommendations")
def get_recommendations(
    keywords: str = Query("", description="Text to search in title/company"),
    skills: str = Query("", description="Comma-separated skills"),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Recommendation logic:
      - if `skills` query param is provided → use that
      - else → use student.skills from DB
      - compute basic text match + skill overlap score (0-100)
    """
    # Determine skill source
    if skills:
        skills_source = skills
    else:
        student = (
            db.query(models.Student)
            .filter(models.Student.user_id == user.id)
            .first()
        )
        skills_source = student.skills if student else ""

    user_skills = _normalize_skills(skills_source)

    internships = db.query(models.Internship).all()
    results = []

    for i in internships:
        base = 10
        text = (i.title or "") + " " + (i.company or "")
        if keywords and keywords.lower() in text.lower():
            base += 20

        required_skills = _normalize_skills(i.required_skills)
        overlap = user_skills & required_skills
        if required_skills:
            overlap_ratio = len(overlap) / len(required_skills)
        else:
            overlap_ratio = 0.0

        score = base + int(overlap_ratio * 70)  # 0–100
        if score > 100:
            score = 100

        results.append(
            {
                "id": i.id,
                "title": i.title,
                "company": i.company,
                "location": i.location,
                "skills": i.required_skills,
                "match": score,
            }
        )

    results.sort(key=lambda x: x["match"], reverse=True)
    return results
