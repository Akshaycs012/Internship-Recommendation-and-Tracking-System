# backend/app/core/paths.py

from pathlib import Path

# This file is in backend/app/core/paths.py
# parents[0] = core
# parents[1] = app
# parents[2] = backend
# parents[3] = project   <-- your root folder

BASE_DIR = Path(__file__).resolve().parents[3]

# frontend/ lives directly under project/
FRONTEND_DIR = BASE_DIR / "frontend"

# uploads/ also directly under project/
UPLOADS_DIR = BASE_DIR / "uploads"
RESUME_DIR = UPLOADS_DIR / "resumes"
TASK_FILES_DIR = UPLOADS_DIR / "tasks"

# ensure folders exist
UPLOADS_DIR.mkdir(exist_ok=True)
RESUME_DIR.mkdir(exist_ok=True)
TASK_FILES_DIR.mkdir(exist_ok=True)
