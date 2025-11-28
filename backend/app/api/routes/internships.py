# backend/app/api/routes/internships.py

from typing import List, Set

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db import models
from app.api.deps import get_current_user

router = APIRouter(prefix="/internships", tags=["internships"])


# ---------- helpers ----------

def _normalize_skills(skills_str: str | None) -> Set[str]:
    """
    Convert a comma separated skill string like 'Python, fastapi, SQL'
    into a lower-cased set: {'python', 'fastapi', 'sql'}.
    """
    if not skills_str:
        return set()
    return {
        s.strip().lower()
        for s in skills_str.split(",")
        if s.strip()
    }


def _tokenize_keywords(keywords: str) -> List[str]:
    """
    Split the free-text 'keywords' into lowercase tokens.
    Example: 'python web dev' -> ['python', 'web', 'dev']
    """
    if not keywords:
        return []
    return [t.lower() for t in keywords.split() if t.strip()]


# ---------- main recommendation / search endpoint ----------

@router.get("/recommendations")
def get_recommendations(
    keywords: str = Query("", description="Search text in title/company/industry"),
    skills: str = Query(
        "",
        description="Comma-separated skills. If empty, use student's profile skills.",
    ),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Internship recommendation + search.

    Behaviour:
    - If `skills` query param is provided -> use that.
    - Else -> use student's saved skills from DB (if any).
    - We always search over all internships created by admin.
    - Match score (0–100) is based on:
        * text match: title, company, industry, description, required_skills
        * skill overlap: intersection between student skills and required_skills
    - Partial matches are supported:
        * 'py' will match 'python' because we search with 'py' substring.
        * Each keyword token contributes to the score if it appears in any field.
    """

    # ----- 1. Determine skill source -----
    if skills:
        skills_source = skills
    else:
        # Try to load student profile; if not a student, fallback to no skills
        student = (
            db.query(models.Student)
            .filter(models.Student.user_id == user.id)
            .first()
        )
        skills_source = student.skills if student and student.skills else ""

    user_skills = _normalize_skills(skills_source)
    keyword_tokens = _tokenize_keywords(keywords)

    # ----- 2. Load all internships from DB -----
    internships = db.query(models.Internship).all()

    results: list[dict] = []

    for i in internships:
        # Build a big lower-cased text blob for text search
        text_blob = " ".join(
            [
                i.title or "",
                i.company or "",
                i.industry or "",
                i.description or "",
                i.required_skills or "",
            ]
        ).lower()

        # ----- text match score (partial matches allowed) -----
        text_hits = 0
        for token in keyword_tokens:
            if token in text_blob:
                text_hits += 1

        # Each hit adds 10 points, up to 40 from text
        text_score = min(text_hits * 10, 40)

        # ----- skill overlap score -----
        required_skills = _normalize_skills(i.required_skills)
        overlap = user_skills & required_skills

        if required_skills:
            overlap_ratio = len(overlap) / len(required_skills)
        else:
            overlap_ratio = 0.0

        # Up to 60 points from skills
        skill_score = int(overlap_ratio * 60)

        base_score = 0
        match_score = base_score + text_score + skill_score
        if match_score > 100:
            match_score = 100

        # ----- Filter: when user typed something, hide totally irrelevant rows -----
        if keyword_tokens:
            if text_hits == 0 and not overlap:
                # no text token found and no skill intersection → skip this internship
                continue

        # We still include internships with match_score 0 when no filters are provided
        results.append(
            {
                "id": i.id,
                "title": i.title,
                "company": i.company,
                "location": i.location,
                "skills": i.required_skills,
                "match": match_score,
            }
        )

    # Sort by match descending so best results appear first
    results.sort(key=lambda x: x["match"], reverse=True)
    return results
