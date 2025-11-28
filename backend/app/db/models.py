# backend/app/db/models.py
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Text,
    Date,
    DateTime,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.database import Base


# ===================== USER TABLE ===================== #
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(String, nullable=False)  # student / mentor / admin

    student = relationship("Student", back_populates="user", uselist=False)
    mentor = relationship("Mentor", back_populates="user", uselist=False)
    admin = relationship("Admin", back_populates="user", uselist=False)

    feedback_given = relationship(
        "MentorFeedback",
        back_populates="mentor_user",
        cascade="all, delete-orphan",
    )


# ===================== STUDENT TABLE ===================== #
class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)

    # existing basic skills field (kept)
    skills = Column(String, default="")  # comma separated skills "python,react"

    # -------- extended profile fields --------
    # age OR date_of_birth – you can use one or both
    age = Column(Integer, nullable=True)
    date_of_birth = Column(Date, nullable=True)

    phone = Column(String, nullable=True)         # mobile number
    education = Column(String, nullable=True)     # degree / year
    experience = Column(Text, nullable=True)      # previous experience, free text

    linkedin_url = Column(String, nullable=True)
    github_url = Column(String, nullable=True)
    portfolio_url = Column(String, nullable=True)

    # simple text for skill level, e.g. "Beginner / Intermediate / Advanced"
    skills_rating = Column(String, default="")

    # resume stored as URL/path so admin can download
    resume_url = Column(String, nullable=True)

    user = relationship("User", back_populates="student")

    applications = relationship(
        "Application",
        back_populates="student",
        cascade="all, delete-orphan",
    )
    feedback = relationship(
        "MentorFeedback",
        back_populates="student",
        cascade="all, delete-orphan",
    )


# ===================== MENTOR TABLE ===================== #
class Mentor(Base):
    __tablename__ = "mentors"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    expertise = Column(String, default="")

    user = relationship("User", back_populates="mentor")


# ===================== ADMIN TABLE ===================== #
class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)

    user = relationship("User", back_populates="admin")


# ===================== INTERNSHIP ===================== #
class Internship(Base):
    __tablename__ = "internships"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    location = Column(String, default="")
    industry = Column(String, default="")
    # unified name used everywhere in backend logic
    required_skills = Column(String, default="")  # e.g. "python,sql,react"
    description = Column(Text, default="")

    applications = relationship(
        "Application",
        back_populates="internship",
        cascade="all, delete-orphan",
    )
    tasks = relationship(
        "InternshipTask",
        back_populates="internship",
        cascade="all, delete-orphan",
    )


# ===================== APPLICATION ===================== #
class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    internship_id = Column(Integer, ForeignKey("internships.id"))

    # existing status – still used
    # values: pending / approved / rejected
    status = Column(String, default="pending")

    # -------- extended lifecycle fields --------
    # when student applied from recommendations
    applied_at = Column(DateTime(timezone=True), server_default=func.now())
    # when admin approved
    approved_at = Column(DateTime(timezone=True), nullable=True)
    # when internship finished/completed
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # progress view: pending / active / completed
    progress_status = Column(String, default="pending")

    # store resume snapshot at the moment of application
    resume_url = Column(String, default="")

    # admin notes / comments
    remarks_admin = Column(Text, default="")

    student = relationship("Student", back_populates="applications")
    internship = relationship("Internship", back_populates="applications")


# ===================== MENTOR FEEDBACK ===================== #
class MentorFeedback(Base):
    __tablename__ = "mentor_feedback"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    mentor_user_id = Column(Integer, ForeignKey("users.id"))
    feedback_text = Column(Text, nullable=False)

    student = relationship("Student", back_populates="feedback")
    mentor_user = relationship("User", back_populates="feedback_given")


# ===================== INTERNSHIP TASKS ===================== #
class InternshipTask(Base):
    __tablename__ = "internship_tasks"

    id = Column(Integer, primary_key=True, index=True)
    internship_id = Column(Integer, ForeignKey("internships.id"), nullable=False)

    title = Column(String, nullable=False)
    description = Column(Text, default="")
    due_date = Column(Date, nullable=False)
    order_index = Column(Integer, default=0)

    internship = relationship("Internship", back_populates="tasks")
    submissions = relationship(
        "TaskSubmission",
        back_populates="task",
        cascade="all, delete-orphan",
    )


# ===================== TASK SUBMISSION ===================== #
class TaskSubmission(Base):
    __tablename__ = "task_submissions"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("internship_tasks.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)

    file_path = Column(String, nullable=False)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, default="on_time")  # on_time / late
    feedback = Column(Text, default="")

    task = relationship("InternshipTask", back_populates="submissions")
    student = relationship("Student")


# ===================== APPLICATION LOG (for Logs page) ===================== #
class ApplicationLog(Base):
    __tablename__ = "application_logs"

    id = Column(Integer, primary_key=True, index=True)

    application_id = Column(Integer, ForeignKey("applications.id"), nullable=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=True)
    internship_id = Column(Integer, ForeignKey("internships.id"), nullable=True)

    event = Column(String, nullable=False)  # applied/approved/rejected/cancelled/completed/created
    message = Column(Text, default="")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
