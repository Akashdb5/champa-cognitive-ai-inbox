"""
Statistics API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from typing import Dict, List

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.message import Message, MessageAnalysis, ActionableItem
from app.models.platform import PlatformConnection
from app.schemas.stats import OverviewStats, ActionableStats, PlatformStats, SpamStats, PriorityDistribution
from app.schemas.reply import SmartReply as SmartReplyModel

router = APIRouter(prefix="/api/stats", tags=["statistics"])


@router.get("/overview", response_model=OverviewStats)
async def get_overview_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get overview statistics for the dashboard.
    
    Returns:
        - Count of new messages received
        - Number of pending draft approvals
        - Count of actionable items with deadlines today
        - Total messages
        - Connected platforms
    
    Validates: Requirements 10.1, 10.2, 10.3
    """
    user_id = current_user.id
    
    # Get new messages count (last 24 hours)
    yesterday = datetime.utcnow() - timedelta(days=1)
    new_messages_count = db.query(func.count(Message.id)).filter(
        Message.user_id == user_id,
        Message.timestamp >= yesterday
    ).scalar() or 0
    
    # Get pending drafts count
    from app.models.message import SmartReply
    pending_drafts_count = db.query(func.count(SmartReply.id)).filter(
        SmartReply.user_id == user_id,
        SmartReply.status == "pending"
    ).scalar() or 0
    
    # Get actionables with deadlines today
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    
    actionables_today_count = db.query(func.count(ActionableItem.id)).filter(
        ActionableItem.user_id == user_id,
        ActionableItem.completed == False,
        ActionableItem.deadline >= today_start,
        ActionableItem.deadline < today_end
    ).scalar() or 0
    
    # Get total messages
    total_messages = db.query(func.count(Message.id)).filter(
        Message.user_id == user_id
    ).scalar() or 0
    
    # Get connected platforms
    connected_platforms_query = db.query(PlatformConnection.platform).filter(
        PlatformConnection.user_id == user_id
    ).all()
    connected_platforms = [p[0] for p in connected_platforms_query]
    
    return OverviewStats(
        new_messages_count=new_messages_count,
        pending_drafts_count=pending_drafts_count,
        actionables_today_count=actionables_today_count,
        total_messages=total_messages,
        connected_platforms=connected_platforms
    )


@router.get("/actionables", response_model=ActionableStats)
async def get_actionable_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get statistics about actionable items.
    
    Returns:
        - Total actionables
        - Completed count
        - Pending count
        - Overdue count
        - Breakdown by type
        - Upcoming deadlines
    
    Validates: Requirements 10.1, 10.2, 10.3
    """
    user_id = current_user.id
    now = datetime.utcnow()
    
    # Get total actionables
    total_actionables = db.query(func.count(ActionableItem.id)).filter(
        ActionableItem.user_id == user_id
    ).scalar() or 0
    
    # Get completed count
    completed_count = db.query(func.count(ActionableItem.id)).filter(
        ActionableItem.user_id == user_id,
        ActionableItem.completed == True
    ).scalar() or 0
    
    # Get pending count
    pending_count = db.query(func.count(ActionableItem.id)).filter(
        ActionableItem.user_id == user_id,
        ActionableItem.completed == False
    ).scalar() or 0
    
    # Get overdue count
    overdue_count = db.query(func.count(ActionableItem.id)).filter(
        ActionableItem.user_id == user_id,
        ActionableItem.completed == False,
        ActionableItem.deadline < now
    ).scalar() or 0
    
    # Get breakdown by type
    type_counts = db.query(
        ActionableItem.type,
        func.count(ActionableItem.id)
    ).filter(
        ActionableItem.user_id == user_id,
        ActionableItem.completed == False
    ).group_by(ActionableItem.type).all()
    
    by_type = {type_name: count for type_name, count in type_counts}
    
    # Get upcoming deadlines (next 7 days)
    next_week = now + timedelta(days=7)
    upcoming = db.query(ActionableItem).filter(
        ActionableItem.user_id == user_id,
        ActionableItem.completed == False,
        ActionableItem.deadline >= now,
        ActionableItem.deadline <= next_week
    ).order_by(ActionableItem.deadline.asc()).limit(10).all()
    
    upcoming_deadlines = [
        {
            "id": str(item.id),
            "description": item.description,
            "type": item.type,
            "deadline": item.deadline.isoformat(),
            "message_id": str(item.message_id)
        }
        for item in upcoming
    ]
    
    return ActionableStats(
        total_actionables=total_actionables,
        completed_count=completed_count,
        pending_count=pending_count,
        overdue_count=overdue_count,
        by_type=by_type,
        upcoming_deadlines=upcoming_deadlines
    )


@router.get("/platforms", response_model=List[PlatformStats])
async def get_platform_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get statistics broken down by platform.
    
    Returns message counts, last sync time, and average priority for each platform.
    """
    user_id = current_user.id
    
    # Get all connected platforms
    connections = db.query(PlatformConnection).filter(
        PlatformConnection.user_id == user_id
    ).all()
    
    platform_stats = []
    
    for connection in connections:
        # Get message count for this platform
        message_count = db.query(func.count(Message.id)).filter(
            Message.user_id == user_id,
            Message.platform == connection.platform
        ).scalar() or 0
        
        # Get average priority score
        avg_priority = db.query(func.avg(MessageAnalysis.priority_score)).join(
            Message, MessageAnalysis.message_id == Message.id
        ).filter(
            Message.user_id == user_id,
            Message.platform == connection.platform
        ).scalar() or 0.0
        
        platform_stats.append(
            PlatformStats(
                platform=connection.platform,
                message_count=message_count,
                last_sync=connection.last_sync_at or connection.connected_at,
                avg_priority=float(avg_priority)
            )
        )
    
    return platform_stats


@router.get("/spam", response_model=SpamStats)
async def get_spam_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get spam detection statistics.
    
    Returns:
        - Total spam count
        - Spam breakdown by type
        - Spam percentage
        - Recent spam messages with unsubscribe links
    """
    user_id = current_user.id
    
    # Get total spam count
    total_spam = db.query(func.count(MessageAnalysis.id)).join(
        Message, MessageAnalysis.message_id == Message.id
    ).filter(
        Message.user_id == user_id,
        MessageAnalysis.is_spam == True
    ).scalar() or 0
    
    # Get total messages for percentage
    total_messages = db.query(func.count(Message.id)).filter(
        Message.user_id == user_id
    ).scalar() or 0
    
    spam_percentage = (total_spam / total_messages * 100) if total_messages > 0 else 0.0
    
    # Get spam breakdown by type
    spam_by_type_query = db.query(
        MessageAnalysis.spam_type,
        func.count(MessageAnalysis.id)
    ).join(
        Message, MessageAnalysis.message_id == Message.id
    ).filter(
        Message.user_id == user_id,
        MessageAnalysis.is_spam == True
    ).group_by(MessageAnalysis.spam_type).all()
    
    spam_by_type = {spam_type: count for spam_type, count in spam_by_type_query}
    
    # Get recent spam with unsubscribe links
    recent_spam_query = db.query(Message, MessageAnalysis).join(
        MessageAnalysis, Message.id == MessageAnalysis.message_id
    ).filter(
        Message.user_id == user_id,
        MessageAnalysis.is_spam == True,
        MessageAnalysis.unsubscribe_link.isnot(None)
    ).order_by(Message.timestamp.desc()).limit(10).all()
    
    recent_spam = [
        {
            "message_id": str(msg.id),
            "sender": msg.sender,
            "subject": msg.subject,
            "spam_type": analysis.spam_type,
            "spam_score": analysis.spam_score,
            "unsubscribe_link": analysis.unsubscribe_link,
            "timestamp": msg.timestamp.isoformat()
        }
        for msg, analysis in recent_spam_query
    ]
    
    return SpamStats(
        total_spam_count=total_spam,
        spam_by_type=spam_by_type,
        spam_percentage=round(spam_percentage, 2),
        recent_spam=recent_spam
    )


@router.get("/priority-distribution", response_model=PriorityDistribution)
async def get_priority_distribution(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get distribution of messages by priority level.
    
    Returns counts for high, medium, and low priority messages.
    """
    user_id = current_user.id
    
    # Get high priority count (0.7-1.0)
    high_priority = db.query(func.count(MessageAnalysis.id)).join(
        Message, MessageAnalysis.message_id == Message.id
    ).filter(
        Message.user_id == user_id,
        MessageAnalysis.priority_score >= 0.7
    ).scalar() or 0
    
    # Get medium priority count (0.4-0.6)
    medium_priority = db.query(func.count(MessageAnalysis.id)).join(
        Message, MessageAnalysis.message_id == Message.id
    ).filter(
        Message.user_id == user_id,
        MessageAnalysis.priority_score >= 0.4,
        MessageAnalysis.priority_score < 0.7
    ).scalar() or 0
    
    # Get low priority count (0.0-0.3)
    low_priority = db.query(func.count(MessageAnalysis.id)).join(
        Message, MessageAnalysis.message_id == Message.id
    ).filter(
        Message.user_id == user_id,
        MessageAnalysis.priority_score < 0.4
    ).scalar() or 0
    
    # Get average priority
    avg_priority = db.query(func.avg(MessageAnalysis.priority_score)).join(
        Message, MessageAnalysis.message_id == Message.id
    ).filter(
        Message.user_id == user_id
    ).scalar() or 0.0
    
    return PriorityDistribution(
        high_priority=high_priority,
        medium_priority=medium_priority,
        low_priority=low_priority,
        avg_priority=float(avg_priority)
    )
