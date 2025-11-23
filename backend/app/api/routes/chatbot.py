from fastapi import APIRouter

router = APIRouter(prefix="/chatbot", tags=["chatbot"])


@router.post("/")
def chat(message: str):
    return {"reply": "AI will respond later. Placeholder."}
