# backend/app/db/models.py
from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(String, nullable=False)  # "student", "mentor", "admin"

    # One-to-one role links
    student = relationship("Student", back_populates="user", uselist=False)
    mentor = relationship("Mentor", back_populates="user", uselist=False)
    admin = relationship("Admin", back_populates="user", uselist=False)

    # For mentor feedback
    feedback_given = relationship(
        "MentorFeedback",
        back_populates="mentor_user",
        cascade="all, delete-orphan",
    )


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    skills = Column(String, default="")

    user = relationship("User", back_populates="student")

    # Student’s applications & feedback
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


class Mentor(Base):
    __tablename__ = "mentors"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    expertise = Column(String, default="")  # e.g. "Backend, AI"

    user = relationship("User", back_populates="mentor")


class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)

    user = relationship("User", back_populates="admin")


class Internship(Base):
    __tablename__ = "internships"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    location = Column(String, default="")
    required_skills = Column(String, default="")
    industry = Column(String, default="")

    applications = relationship(
        "Application",
        back_populates="internship",
        cascade="all, delete-orphan",
    )


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    internship_id = Column(Integer, ForeignKey("internships.id"))
    status = Column(String, default="pending")

    student = relationship("Student", back_populates="applications")
    internship = relationship("Internship", back_populates="applications")


class MentorFeedback(Base):
    __tablename__ = "mentor_feedback"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    mentor_user_id = Column(Integer, ForeignKey("users.id"))
    feedback_text = Column(Text, nullable=False)

    student = relationship("Student", back_populates="feedback")
    mentor_user = relationship("User", back_populates="feedback_given")
