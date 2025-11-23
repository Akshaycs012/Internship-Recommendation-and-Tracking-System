from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.db import models

router = APIRouter(prefix="/progress", tags=["progress"])


@router.post("/upload")
def upload_deliverable(
    file: UploadFile,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    # dummy storage
    return {"message": f"Received file {file.filename}"}
