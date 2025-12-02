"""
Authentication schemas for Auth0
"""
from pydantic import BaseModel
from typing import Optional


class AuthResponse(BaseModel):
    """Authentication response with user info from Auth0"""
    user_id: str
    email: str
    username: Optional[str] = None
    access_token: str
