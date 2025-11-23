from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import Base, engine
from app.api.routes import (
    auth, students, internships, applications,
    progress, mentor, admin, chatbot
)

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(students.router)
app.include_router(internships.router)
app.include_router(applications.router)
app.include_router(progress.router)
app.include_router(mentor.router)
app.include_router(admin.router)
app.include_router(chatbot.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
