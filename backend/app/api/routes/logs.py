from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.api.deps import require_admin
from app.db import models

router = APIRouter(prefix="/logs",tags=["logs"])

@router.get("/")
def all_logs(db:Session=Depends(get_db),admin=Depends(require_admin)):
    logs=db.query(models.ApplicationLog).order_by(models.ApplicationLog.id.desc()).all()
    return [{
        "event":l.event,
        "student_id":l.student_id,
        "internship_id":l.internship_id,
        "message":l.message,
        "time":l.created_at
    } for l in logs]
