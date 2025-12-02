"""
Application configuration and settings
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore"
    }
    
    # Database
    DATABASE_URL: str = "postgresql://champa:champa_password@localhost:5432/champa"
    
    # Auth0
    AUTH0_DOMAIN: str = ""
    AUTH0_API_AUDIENCE: str = ""
    AUTH0_CLIENT_ID: str = ""
    AUTH0_CLIENT_SECRET: str = ""
    
    # OpenAI
    OPENAI_API_KEY: str = ""
    
    # Google OAuth (for Gmail and Calendar)
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/platforms/gmail/callback"
    GOOGLE_CALENDAR_REDIRECT_URI: str = "http://localhost:8000/api/platforms/calendar/callback"
    
    # Slack OAuth
    SLACK_CLIENT_ID: str = ""
    SLACK_CLIENT_SECRET: str = ""
    SLACK_REDIRECT_URI: str = "http://localhost:8000/api/platforms/slack/callback"
    
    # Qdrant
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: Optional[str] = None
    
    # Application
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ENVIRONMENT: str = "development"
    FRONTEND_URL: str = "http://localhost:3000"  # Frontend URL for OAuth redirects


settings = Settings()
