# backend/app/main.py

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse

from app.db.database import Base, engine
from app.api.routes import (
    auth, students, internships, applications,
    progress, mentor, admin, chatbot
)

# ==== Paths ====
BASE_DIR      = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
FRONTEND_DIR  = os.path.join(BASE_DIR, "frontend")
UPLOADS_DIR   = os.path.join(BASE_DIR, "uploads")

os.makedirs(UPLOADS_DIR, exist_ok=True)
Base.metadata.create_all(bind=engine)

# ==== App ====
app = FastAPI(title="Internship Portal API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==== Static Serving (fixed) ====
app.mount("/static",  StaticFiles(directory=os.path.join(FRONTEND_DIR, "assets")), name="static")
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")

# ==== Serve HTML Pages ====
@app.get("/", response_class=HTMLResponse)
def serve_home():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

@app.get("/{page}", response_class=HTMLResponse)
def serve_page(page: str):
    file = os.path.join(FRONTEND_DIR, page)
    return FileResponse(file) if os.path.exists(file) else HTMLResponse("404", status_code=404)

# ==== API Routes ====
app.include_router(auth.router)
app.include_router(students.router)
app.include_router(internships.router)
app.include_router(applications.router)
app.include_router(progress.router)
app.include_router(mentor.router)
app.include_router(admin.router)
app.include_router(chatbot.router)

@app.get("/health")
def health():
    return {"status": "ok"}
