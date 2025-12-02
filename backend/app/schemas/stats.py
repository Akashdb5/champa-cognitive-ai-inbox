"""
Statistics schemas
"""
from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime


class OverviewStats(BaseModel):
    """Overview statistics for dashboard"""
    new_messages_count: int
    pending_drafts_count: int
    actionables_today_count: int
    total_messages: int
    connected_platforms: List[str]


class ActionableStats(BaseModel):
    """Statistics about actionable items"""
    total_actionables: int
    completed_count: int
    pending_count: int
    overdue_count: int
    by_type: Dict[str, int]
    upcoming_deadlines: List[Dict[str, Any]]


class PlatformStats(BaseModel):
    """Statistics for a specific platform"""
    platform: str
    message_count: int
    last_sync: datetime
    avg_priority: float


class SpamStats(BaseModel):
    """Statistics about spam detection"""
    total_spam_count: int
    spam_by_type: Dict[str, int]
    spam_percentage: float
    recent_spam: List[Dict[str, Any]]


class PriorityDistribution(BaseModel):
    """Distribution of messages by priority"""
    high_priority: int  # 0.7-1.0
    medium_priority: int  # 0.4-0.6
    low_priority: int  # 0.0-0.3
    avg_priority: float
