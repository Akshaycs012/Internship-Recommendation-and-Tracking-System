# backend/app/core/config.py

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Internship Portal"

    # Using SQLite for local dev
    DATABASE_URL: str = "sqlite:///./internship.db"

    JWT_SECRET_KEY: str = "supersecretkey"  # change in production
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    model_config = {
        "env_file": ".env"
    }


settings = Settings()
