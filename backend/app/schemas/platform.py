"""
Platform connection schemas
"""
from pydantic import BaseModel
from typing import Optional


class PlatformConnectionResponse(BaseModel):
    """Response after platform connection"""
    platform: str
    status: str  # 'pending', 'connected', 'disconnected'
    message: str
    redirect_url: Optional[str] = None  # OAuth redirect URL for user authorization
    connection_request_id: Optional[str] = None  # Temporary ID for pending connections


class PlatformStatus(BaseModel):
    """Status of all platform connections"""
    gmail: bool = False
    slack: bool = False
    calendar: bool = False
