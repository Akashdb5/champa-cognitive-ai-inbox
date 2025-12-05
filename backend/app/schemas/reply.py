"""
Smart reply Pydantic schemas
"""
from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime
from uuid import UUID


class SmartReply(BaseModel):
    """Smart reply draft"""
    id: Optional[UUID] = None
    message_id: UUID
    user_id: UUID
    draft_content: str
    status: Literal["pending", "approved", "rejected", "sent", "suggestion"]
    created_at: datetime
    reviewed_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    
    # Message context for display
    message_subject: Optional[str] = None
    message_sender: Optional[str] = None
    message_platform: Optional[str] = None
    message_preview: Optional[str] = None
    
    class Config:
        from_attributes = True


class SmartReplyRequest(BaseModel):
    """Request to generate a smart reply"""
    message_id: UUID


class SmartReplyApproval(BaseModel):
    """Approve a smart reply"""
    approved: Optional[bool] = True


class SmartReplyEdit(BaseModel):
    """Edit a smart reply draft"""
    draft_content: str


class SmartReplyRejection(BaseModel):
    """Reject a smart reply"""
    reason: Optional[str] = None


class SmartReplyResponse(BaseModel):
    """Response after smart reply action"""
    id: UUID
    status: Literal["pending", "approved", "rejected", "sent"]
    message: str
    
    class Config:
        from_attributes = True
