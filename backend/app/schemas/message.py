"""
Message-related Pydantic schemas
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any, Literal, List
from datetime import datetime
from uuid import UUID


class NormalizedMessage(BaseModel):
    """Unified message format across all platforms"""
    id: Optional[UUID] = None
    user_id: UUID
    platform: Literal["gmail", "slack", "calendar"]
    platform_message_id: str
    sender: str
    content: str
    subject: Optional[str] = None
    timestamp: datetime
    thread_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        from_attributes = True


class MessageAnalysis(BaseModel):
    """AI analysis results for a message"""
    message_id: UUID
    summary: str
    intent: str
    priority_score: float = Field(ge=0.0, le=1.0)
    is_spam: bool = False
    spam_score: float = Field(default=0.0, ge=0.0, le=1.0)
    spam_type: str = "none"
    unsubscribe_link: Optional[str] = None
    tasks: List[Dict[str, Any]] = Field(default_factory=list)
    deadlines: List[Dict[str, Any]] = Field(default_factory=list)
    
    @field_validator('priority_score')
    @classmethod
    def validate_priority(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError('priority_score must be between 0.0 and 1.0')
        return v
    
    @field_validator('spam_score')
    @classmethod
    def validate_spam_score(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError('spam_score must be between 0.0 and 1.0')
        return v
    
    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    """Message with analysis for API responses"""
    id: UUID
    user_id: UUID
    platform: str
    sender: str
    content: str
    subject: Optional[str] = None
    timestamp: datetime
    thread_id: Optional[str] = None
    summary: Optional[str] = None
    intent: Optional[str] = None
    priority_score: Optional[float] = None
    is_spam: Optional[bool] = None
    spam_score: Optional[float] = None
    spam_type: Optional[str] = None
    unsubscribe_link: Optional[str] = None
    actionable_items: List[Dict[str, Any]] = Field(default_factory=list)
    
    class Config:
        from_attributes = True


class MessageFilters(BaseModel):
    """Filters for querying messages"""
    platform: Optional[Literal["gmail", "slack", "calendar"]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    min_priority: Optional[float] = Field(None, ge=0.0, le=1.0)
    has_actionables: Optional[bool] = None
    limit: int = Field(50, ge=1, le=100)
    offset: int = Field(0, ge=0)


class ThreadContext(BaseModel):
    """Full conversation thread context"""
    thread_id: str
    messages: List[NormalizedMessage]
    participant_count: int
    start_time: datetime
    last_update: datetime


class MessageSearchRequest(BaseModel):
    """Request for semantic message search"""
    query: str = Field(..., min_length=1, description="Search query")
    limit: Optional[int] = Field(10, ge=1, le=50, description="Maximum number of results")


class MessageSearchResponse(BaseModel):
    """Response from semantic message search"""
    query: str
    results: List[NormalizedMessage]
    total_count: int
