from typing import List, Set
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db import models
from app.api.deps import get_current_user

router = APIRouter(prefix="/internships", tags=["internships"])


# ================= NORMALIZE SKILL STRINGS =================
def _normalize_skills(skills_str: str | None) -> Set[str]:
    if not skills_str:
        return set()
    return {s.strip().lower() for s in skills_str.split(",") if s.strip()}


# ================= KEYWORD TOKENIZER =================
def _tokenize_keywords(keywords: str) -> List[str]:
    if not keywords:
        return []
    return [t.lower() for t in keywords.split() if t.strip()]


# ================= RECOMMENDATION + SEARCH =================
@router.get("/recommendations")
def get_recommendations(
    keywords: str = Query("", description="Search title/company/industry"),
    skills: str = Query("", description="comma skills OR auto from student"),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    try:
        # 1) Get student skills or override if search input is provided
        if skills:
            skills_source = skills
        else:
            student = db.query(models.Student).filter(models.Student.user_id == user.id).first()
            skills_source = student.skills if student else ""

        user_skills = _normalize_skills(skills_source)
        keyword_tokens = _tokenize_keywords(keywords)

        # 2) Load all internships
        internships = db.query(models.Internship).all()
        results = []

        # 3) Match scoring
        for i in internships:
            text_blob = " ".join([
                i.title or "",
                i.company or "",
                i.industry or "",
                i.description or "",
                i.required_skills or "",
            ]).lower()

            text_hits = sum(1 for token in keyword_tokens if token in text_blob)
            text_score = min(text_hits * 10, 40)

            required = _normalize_skills(i.required_skills)
            overlap = user_skills & required
            overlap_ratio = len(overlap) / len(required) if required else 0
            skill_score = int(overlap_ratio * 60)

            match = min(text_score + skill_score, 100)

            if keyword_tokens and text_hits == 0 and not overlap:
                continue  # filter irrelevant

            results.append({
                "id": i.id,
                "title": i.title,
                "company": i.company,
                "location": i.location,
                "skills": i.required_skills,
                "match": match,
            })

        results.sort(key=lambda x: x["match"], reverse=True)
        return results

    except Exception as e:
        print("ERROR /internships/recommendations →", e)
        return []
