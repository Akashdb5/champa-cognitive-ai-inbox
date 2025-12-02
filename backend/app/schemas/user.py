"""
User and persona Pydantic schemas
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    username: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    timezone: Optional[str] = None
    website: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a user"""
    auth0_id: str


class UserUpdate(BaseModel):
    """Schema for updating user profile"""
    phone: Optional[str] = None
    location: Optional[str] = None
    timezone: Optional[str] = None
    website: Optional[str] = None


class User(UserBase):
    """User schema for responses"""
    id: UUID
    auth0_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserPersona(BaseModel):
    """User persona memory entry"""
    id: Optional[UUID] = None
    user_id: UUID
    memory_key: str
    memory_value: Dict[str, Any]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class StylePatterns(BaseModel):
    """Communication style patterns"""
    tone: str
    formality: str
    common_phrases: List[str]
    signature: Optional[str] = None


class Contact(BaseModel):
    """Contact relationship information"""
    email: str
    name: Optional[str] = None
    relationship: str
    interaction_count: int
    last_interaction: datetime


class Preferences(BaseModel):
    """User preferences for message handling"""
    auto_reply_enabled: bool = False
    priority_threshold: float = 0.5
    notification_settings: Dict[str, bool] = {}
    preferred_response_time: Optional[str] = None


class UserPersonaData(BaseModel):
    """Complete user persona data"""
    user_id: UUID
    style_patterns: Optional[StylePatterns] = None
    contacts: List[Contact] = []
    preferences: Optional[Preferences] = None
