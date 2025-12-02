"""
Smart Reply API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas.reply import (
    SmartReply,
    SmartReplyRequest,
    SmartReplyApproval,
    SmartReplyEdit,
    SmartReplyRejection,
    SmartReplyResponse
)
from app.services.reply import get_reply_service


router = APIRouter(prefix="/api/replies", tags=["replies"])


@router.post("/generate", response_model=SmartReply, status_code=status.HTTP_201_CREATED)
async def generate_smart_reply(
    request: SmartReplyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a smart reply for a message
    
    This endpoint:
    1. Fetches the thread context
    2. Retrieves user persona
    3. Uses deep agent to generate a draft reply
    4. Stores as pending for approval
    
    Validates: Requirements 7.1, 7.2, 7.4, 7.5
    """
    try:
        reply_service = get_reply_service(db)
        smart_reply = await reply_service.generate_smart_reply(
            message_id=request.message_id,
            user_id=current_user.id
        )
        return smart_reply
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate reply: {str(e)}"
        )


@router.get("/pending", response_model=List[SmartReply])
async def get_pending_replies(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all pending smart replies for the current user
    
    Validates: Requirements 8.1
    """
    reply_service = get_reply_service(db)
    return reply_service.get_pending_replies(current_user.id)


@router.get("/{reply_id}", response_model=SmartReply)
async def get_reply(
    reply_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific smart reply
    """
    reply_service = get_reply_service(db)
    smart_reply = reply_service.get_reply(reply_id, current_user.id)
    
    if not smart_reply:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reply not found")
    
    return smart_reply


@router.put("/{reply_id}/approve", response_model=SmartReplyResponse)
async def approve_reply(
    reply_id: UUID,
    approval: SmartReplyApproval,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Approve a smart reply and send it
    
    This implements the human-in-the-loop approval workflow.
    Upon approval, the reply is sent via the appropriate platform.
    
    Validates: Requirements 8.3
    """
    try:
        reply_service = get_reply_service(db)
        smart_reply = await reply_service.approve_reply(reply_id, current_user.id)
        
        return SmartReplyResponse(
            id=smart_reply.id,
            status=smart_reply.status,
            message="Reply approved and sent successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to approve reply: {str(e)}"
        )


@router.put("/{reply_id}/edit", response_model=SmartReply)
async def edit_reply(
    reply_id: UUID,
    edit: SmartReplyEdit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Edit a smart reply draft
    
    The edited draft remains in pending status for re-approval.
    
    Validates: Requirements 8.4
    """
    try:
        reply_service = get_reply_service(db)
        smart_reply = await reply_service.edit_reply(
            reply_id,
            current_user.id,
            edit.draft_content
        )
        return smart_reply
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to edit reply: {str(e)}"
        )


@router.put("/{reply_id}/reject", response_model=SmartReplyResponse)
async def reject_reply(
    reply_id: UUID,
    rejection: SmartReplyRejection,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Reject a smart reply
    
    The rejected draft is discarded and the user can request a new one.
    
    Validates: Requirements 8.5
    """
    try:
        reply_service = get_reply_service(db)
        smart_reply = await reply_service.reject_reply(reply_id, current_user.id)
        
        return SmartReplyResponse(
            id=smart_reply.id,
            status=smart_reply.status,
            message="Reply rejected successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reject reply: {str(e)}"
        )


@router.post("/suggestions/{suggestion_id}/use")
async def use_suggestion(
    suggestion_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Convert a quick reply suggestion into a pending draft for review/send.
    
    This promotes a suggestion (status='suggestion') to pending (status='pending')
    so the user can review, edit, and send it.
    """
    from app.models.message import SmartReply
    
    # Get the suggestion
    suggestion = db.query(SmartReply).filter(
        SmartReply.id == suggestion_id,
        SmartReply.user_id == current_user.id,
        SmartReply.status == "suggestion"
    ).first()
    
    if not suggestion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Suggestion not found"
        )
    
    # Update status to pending
    suggestion.status = "pending"
    db.commit()
    db.refresh(suggestion)
    
    return {
        "id": str(suggestion.id),
        "message_id": str(suggestion.message_id),
        "draft_content": suggestion.draft_content,
        "status": suggestion.status,
        "message": "Suggestion promoted to pending draft"
    }


@router.delete("/suggestions/{suggestion_id}")
async def delete_suggestion(
    suggestion_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a quick reply suggestion.
    """
    from app.models.message import SmartReply
    
    # Get the suggestion
    suggestion = db.query(SmartReply).filter(
        SmartReply.id == suggestion_id,
        SmartReply.user_id == current_user.id,
        SmartReply.status == "suggestion"
    ).first()
    
    if not suggestion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Suggestion not found"
        )
    
    db.delete(suggestion)
    db.commit()
    
    return {"message": "Suggestion deleted successfully"}
