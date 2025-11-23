from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import Base, engine
from app.db import models

from app.api.routes import (
    auth,
    students,
    internships,
    applications,
    progress,
    mentor,
    admin,
    chatbot,
)

# ✅ Correct table creation
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Internship Portal API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os


frontend_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
)

# Serve assets folder
app.mount("/assets", StaticFiles(directory=os.path.join(frontend_path, "assets")), name="assets")

@app.get("/")
def serve_index():
    return FileResponse(os.path.join(frontend_path, "index.html"))

@app.get("/{page}")
def serve_page(page: str):
    file_path = os.path.join(frontend_path, page)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"detail": "Not Found"}


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
