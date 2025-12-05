"""
Message API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.services.message import MessageService
from app.schemas.message import (
    NormalizedMessage,
    MessageFilters,
    ThreadContext,
    MessageSearchRequest,
    MessageSearchResponse
)
from app.ai.embeddings.qdrant_client import get_qdrant_client

router = APIRouter(prefix="/api/messages", tags=["messages"])


def get_message_service() -> MessageService:
    """Dependency to get message service"""
    return MessageService()


@router.post("/sync")
async def sync_messages(
    platform: Optional[str] = None,
    analyze: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    message_service: MessageService = Depends(get_message_service)
):
    """
    Sync messages from connected platforms and store in database.
    
    Fetches new messages since last sync and stores them.
    For first-time sync, fetches the latest 50 messages.
    Optionally runs AI analysis on new messages.
    
    Args:
        platform: Optional platform to sync (gmail, slack, calendar). If None, syncs all.
        analyze: Whether to run AI analysis on new messages (default: True)
    
    Returns:
        Sync status with count of new messages and analysis results
    """
    import logging
    from app.services.ai import AIService
    
    logger = logging.getLogger(__name__)
    
    try:
        # Fetch new messages from platforms
        normalized_messages = await message_service.fetch_new_messages(
            user_id=current_user.id,
            db=db,
            platform=platform
        )
        
        # Store messages in database and collect stored messages for analysis
        stored_count = 0
        duplicate_count = 0
        analyzed_count = 0
        analysis_failed_count = 0
        messages_to_analyze = []
        
        for msg in normalized_messages:
            try:
                message_id = message_service.store_message(msg, db)
                if message_id:
                    stored_count += 1
                    # Set the message ID for analysis
                    msg.id = message_id
                    messages_to_analyze.append(msg)
                else:
                    duplicate_count += 1
            except Exception as e:
                logger.error(f"Failed to store message: {e}")
                duplicate_count += 1
                continue
        
        # Run AI analysis on stored messages if requested
        if analyze and messages_to_analyze:
            logger.info(f"Analyzing {len(messages_to_analyze)} new messages...")
            ai_service = AIService(db)
            
            for msg in messages_to_analyze:
                try:
                    await ai_service.analyze_message(msg)
                    analyzed_count += 1
                    logger.info(f"Analyzed message {msg.id}")
                except Exception as e:
                    logger.error(f"Failed to analyze message {msg.id}: {e}")
                    analysis_failed_count += 1
                    continue
        
        return {
            "status": "success",
            "platform": platform or "all",
            "new_messages": stored_count,
            "duplicates": duplicate_count,
            "total_fetched": len(normalized_messages),
            "analyzed": analyzed_count,
            "analysis_failed": analysis_failed_count
        }
        
    except Exception as e:
        logger.error(f"Message sync failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync messages: {str(e)}"
        )


@router.post("/list", response_model=List[NormalizedMessage])
async def get_messages(
    filters: MessageFilters,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    message_service: MessageService = Depends(get_message_service)
):
    """
    Get messages for the current user with optional filters.
    
    Returns a unified feed of messages from all connected platforms.
    Can filter out spam and by priority level.
    
    Validates: Requirements 9.1, 12.5
    """
    from app.models.message import Message, MessageAnalysis
    
    # Build query with joins for filtering
    query = db.query(Message).filter(Message.user_id == current_user.id)
    
    # Apply platform filter
    if filters.platform:
        query = query.filter(Message.platform == filters.platform)
    
    # Apply date filters
    if filters.start_date:
        query = query.filter(Message.timestamp >= filters.start_date)
    if filters.end_date:
        query = query.filter(Message.timestamp <= filters.end_date)
    
    # Apply spam filter
    if filters.exclude_spam:
        query = query.outerjoin(MessageAnalysis, Message.id == MessageAnalysis.message_id)
        query = query.filter(
            (MessageAnalysis.is_spam == False) | (MessageAnalysis.is_spam.is_(None))
        )
    
    # Apply priority filter
    if filters.min_priority is not None:
        if not filters.exclude_spam:  # Join if not already joined
            query = query.outerjoin(MessageAnalysis, Message.id == MessageAnalysis.message_id)
        query = query.filter(MessageAnalysis.priority_score >= filters.min_priority)
    
    # Order and paginate
    query = query.order_by(Message.timestamp.desc())
    query = query.offset(filters.offset or 0).limit(filters.limit or 50)
    
    messages = query.all()
    
    # Convert to NormalizedMessage schemas
    normalized_messages = [
        NormalizedMessage(
            id=msg.id,
            user_id=msg.user_id,
            platform=msg.platform,
            platform_message_id=msg.platform_message_id,
            sender=msg.sender,
            content=msg.content,
            subject=msg.subject,
            timestamp=msg.timestamp,
            thread_id=msg.thread_id,
            metadata=msg.platform_metadata or {}
        )
        for msg in messages
    ]
    
    return normalized_messages


@router.get("/{message_id}", response_model=NormalizedMessage)
async def get_message(
    message_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific message by ID.
    
    Validates: Requirements 9.1
    """
    from app.models.message import Message
    
    # Get message
    message = db.query(Message).filter(
        Message.id == message_id,
        Message.user_id == current_user.id
    ).first()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # Convert to NormalizedMessage
    return NormalizedMessage(
        id=message.id,
        user_id=message.user_id,
        platform=message.platform,
        platform_message_id=message.platform_message_id,
        sender=message.sender,
        content=message.content,
        subject=message.subject,
        timestamp=message.timestamp,
        thread_id=message.thread_id,
        metadata=message.platform_metadata or {}
    )


@router.get("/{message_id}/thread", response_model=ThreadContext)
async def get_message_thread(
    message_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    message_service: MessageService = Depends(get_message_service)
):
    """
    Get the full thread context for a message.
    
    Returns all messages in the same thread, ordered chronologically.
    
    Validates: Requirements 7.1
    """
    # Verify message belongs to user
    from app.models.message import Message
    message = db.query(Message).filter(
        Message.id == message_id,
        Message.user_id == current_user.id
    ).first()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # Get thread context
    thread_context = message_service.get_thread_context(
        message_id=message_id,
        db=db
    )
    
    if not thread_context:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thread not found or message has no thread"
        )
    
    return thread_context


@router.post("/search", response_model=MessageSearchResponse)
async def search_messages(
    request: MessageSearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Perform semantic search over messages using Qdrant.
    
    Uses vector embeddings to find messages similar to the search query.
    
    Validates: Requirements 13.4, 13.5
    """
    try:
        # Get Qdrant client
        qdrant_client = get_qdrant_client()
        
        # Perform semantic search
        search_results = await qdrant_client.search_messages(
            user_id=str(current_user.id),
            query=request.query,
            limit=request.limit or 10
        )
        
        # Get full message data from PostgreSQL
        from app.models.message import Message
        message_ids = [UUID(result["message_id"]) for result in search_results]
        
        messages = db.query(Message).filter(
            Message.id.in_(message_ids),
            Message.user_id == current_user.id
        ).all()
        
        # Create a mapping for ordering by relevance
        message_map = {str(msg.id): msg for msg in messages}
        
        # Order messages by search relevance
        ordered_messages = []
        for result in search_results:
            msg_id = result["message_id"]
            if msg_id in message_map:
                msg = message_map[msg_id]
                ordered_messages.append(
                    NormalizedMessage(
                        id=msg.id,
                        user_id=msg.user_id,
                        platform=msg.platform,
                        platform_message_id=msg.platform_message_id,
                        sender=msg.sender,
                        content=msg.content,
                        subject=msg.subject,
                        timestamp=msg.timestamp,
                        thread_id=msg.thread_id,
                        metadata=msg.platform_metadata or {}
                    )
                )
        
        return MessageSearchResponse(
            query=request.query,
            results=ordered_messages,
            total_count=len(ordered_messages)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@router.post("/{message_id}/unsubscribe")
async def unsubscribe_from_sender(
    message_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get unsubscribe link for a spam message.
    
    Returns the unsubscribe URL if available for promotional/newsletter spam.
    User can then open this link to unsubscribe from the sender.
    
    Returns:
        - unsubscribe_link: URL to unsubscribe
        - spam_type: Type of spam
        - sender: Email sender
    """
    from app.models.message import Message, MessageAnalysis
    
    # Get message and analysis
    message = db.query(Message).filter(
        Message.id == message_id,
        Message.user_id == current_user.id
    ).first()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    analysis = db.query(MessageAnalysis).filter(
        MessageAnalysis.message_id == message_id
    ).first()
    
    if not analysis or not analysis.is_spam:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message is not marked as spam"
        )
    
    if not analysis.unsubscribe_link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No unsubscribe link found for this message"
        )
    
    return {
        "unsubscribe_link": analysis.unsubscribe_link,
        "spam_type": analysis.spam_type,
        "sender": message.sender,
        "subject": message.subject
    }


@router.get("/{message_id}/analysis")
async def get_message_analysis(
    message_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get AI analysis for a specific message.
    
    Returns summary, intent, priority, spam detection, and actionable items.
    """
    from app.models.message import Message, MessageAnalysis, ActionableItem
    
    # Verify message belongs to user
    message = db.query(Message).filter(
        Message.id == message_id,
        Message.user_id == current_user.id
    ).first()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # Get analysis
    analysis = db.query(MessageAnalysis).filter(
        MessageAnalysis.message_id == message_id
    ).first()
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found for this message"
        )
    
    # Get actionable items
    actionables = db.query(ActionableItem).filter(
        ActionableItem.message_id == message_id
    ).all()
    
    return {
        "message_id": str(message_id),
        "summary": analysis.summary,
        "intent": analysis.intent,
        "priority_score": analysis.priority_score,
        "is_spam": analysis.is_spam,
        "spam_score": analysis.spam_score,
        "spam_type": analysis.spam_type,
        "unsubscribe_link": analysis.unsubscribe_link,
        "actionable_items": [
            {
                "id": str(item.id),
                "type": item.type,
                "description": item.description,
                "deadline": item.deadline.isoformat() if item.deadline else None,
                "completed": item.completed
            }
            for item in actionables
        ],
        "analyzed_at": analysis.analyzed_at.isoformat()
    }



@router.get("/{message_id}/replies")
async def get_message_replies(
    message_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get smart reply suggestions for a message.
    
    Returns quick reply suggestions generated during analysis.
    """
    from app.models.message import Message, SmartReply
    
    # Verify message belongs to user
    message = db.query(Message).filter(
        Message.id == message_id,
        Message.user_id == current_user.id
    ).first()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # Get smart replies
    replies = db.query(SmartReply).filter(
        SmartReply.message_id == message_id,
        SmartReply.status == "suggestion"
    ).all()
    
    return {
        "message_id": str(message_id),
        "replies": [
            {
                "id": str(reply.id),
                "draft_content": reply.draft_content,
                "status": reply.status,
                "created_at": reply.created_at.isoformat()
            }
            for reply in replies
        ]
    }


@router.post("/analyze-all")
async def analyze_all_messages(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze all messages that don't have analysis yet.
    
    This is useful for:
    - Analyzing messages synced before AI analysis was implemented
    - Re-analyzing messages after AI improvements
    - Fixing failed analyses
    
    Returns:
        Count of messages analyzed and any failures
    """
    import logging
    from app.services.ai import AIService
    from app.models.message import Message, MessageAnalysis
    
    logger = logging.getLogger(__name__)
    
    try:
        # Find messages without analysis
        messages_without_analysis = db.query(Message).outerjoin(
            MessageAnalysis, Message.id == MessageAnalysis.message_id
        ).filter(
            Message.user_id == current_user.id,
            MessageAnalysis.id.is_(None)
        ).all()
        
        if not messages_without_analysis:
            return {
                "status": "success",
                "message": "All messages already analyzed",
                "analyzed": 0,
                "failed": 0
            }
        
        logger.info(f"Found {len(messages_without_analysis)} messages to analyze")
        
        # Analyze each message
        ai_service = AIService(db)
        analyzed_count = 0
        failed_count = 0
        
        for msg in messages_without_analysis:
            try:
                # Convert to NormalizedMessage
                from app.schemas.message import NormalizedMessage
                normalized = NormalizedMessage(
                    id=msg.id,
                    user_id=msg.user_id,
                    platform=msg.platform,
                    platform_message_id=msg.platform_message_id,
                    sender=msg.sender,
                    content=msg.content,
                    subject=msg.subject,
                    timestamp=msg.timestamp,
                    thread_id=msg.thread_id,
                    metadata=msg.platform_metadata or {}
                )
                
                await ai_service.analyze_message(normalized)
                analyzed_count += 1
                
                if analyzed_count % 10 == 0:
                    logger.info(f"Analyzed {analyzed_count}/{len(messages_without_analysis)} messages")
                
            except Exception as e:
                logger.error(f"Failed to analyze message {msg.id}: {e}")
                failed_count += 1
                continue
        
        return {
            "status": "success",
            "total_messages": len(messages_without_analysis),
            "analyzed": analyzed_count,
            "failed": failed_count
        }
        
    except Exception as e:
        logger.error(f"Bulk analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze messages: {str(e)}"
        )
