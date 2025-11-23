# backend/app/api/routes/chatbot.py

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.db import models

router = APIRouter(prefix="/chatbot", tags=["chatbot"])


class ChatMessage(BaseModel):
    message: str


@router.post("/")
def chat(
    payload: ChatMessage,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    # Store user message
    user_log = models.ChatLog(
        user_id=user.id,
        sender_role="user",
        message=payload.message,
    )
    db.add(user_log)

    # Very simple bot reply for now
    reply_text = (
        "This is a placeholder AI response. "
        "Later we will connect a real model for internship guidance."
    )

    bot_log = models.ChatLog(
        user_id=user.id,
        sender_role="bot",
        message=reply_text,
    )
    db.add(bot_log)
    db.commit()

    return {"reply": reply_text}
