"""
Chat assistant schemas
"""
from pydantic import BaseModel
from typing import List, Literal
from datetime import datetime


class ChatRequest(BaseModel):
    """Request to send a chat message"""
    message: str


class ChatResponse(BaseModel):
    """Response from chat assistant"""
    message: str
    timestamp: datetime


class ChatMessage(BaseModel):
    """A single chat message"""
    role: Literal["user", "assistant"]
    content: str
    timestamp: datetime


class ChatHistory(BaseModel):
    """Chat conversation history"""
    messages: List[ChatMessage]
    user_id: str
    total_count: int
