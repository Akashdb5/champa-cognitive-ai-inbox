"""
Chat Assistant API Endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse, ChatHistory, ChatMessage
from app.ai.agents.chat import get_chat_agent
from app.services.message import MessageService
from app.ai.memory.persona_store import get_persona_store
from datetime import datetime

router = APIRouter(prefix="/api/chat", tags=["chat"])

# In-memory storage for chat history (in production, use database or Redis)
_chat_histories = {}


@router.post("/message", response_model=ChatResponse)
async def send_chat_message(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send a message to the chat assistant and get a response.
    
    Validates: Requirements 11.1, 11.2, 11.4
    """
    try:
        # Get or create chat history for this user
        user_id = str(current_user.id)
        if user_id not in _chat_histories:
            _chat_histories[user_id] = []
        
        # Get conversation history
        conversation_history = _chat_histories[user_id]
        
        # Create chat agent
        message_service = MessageService()
        persona_store = get_persona_store(db)
        chat_agent = get_chat_agent(db, message_service, persona_store)
        
        # Process the query
        response_text = await chat_agent.process_query(
            user_id=user_id,
            query=request.message,
            conversation_history=conversation_history
        )
        
        # Store in history
        _chat_histories[user_id].append({
            "role": "user",
            "content": request.message
        })
        _chat_histories[user_id].append({
            "role": "assistant",
            "content": response_text
        })
        
        # Keep only last 20 messages (10 exchanges)
        if len(_chat_histories[user_id]) > 20:
            _chat_histories[user_id] = _chat_histories[user_id][-20:]
        
        return ChatResponse(
            message=response_text,
            timestamp=datetime.utcnow()
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process chat message: {str(e)}"
        )


@router.get("/history", response_model=ChatHistory)
async def get_chat_history(
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    """
    Get chat conversation history for the current user.
    
    Validates: Requirements 11.4
    """
    user_id = str(current_user.id)
    
    # Get history from memory
    history = _chat_histories.get(user_id, [])
    
    # Apply limit
    if len(history) > limit:
        history = history[-limit:]
    
    # Convert to ChatMessage objects
    messages = [
        ChatMessage(
            role=msg["role"],
            content=msg["content"],
            timestamp=datetime.utcnow()  # In production, store actual timestamps
        )
        for msg in history
    ]
    
    return ChatHistory(
        messages=messages,
        user_id=user_id,
        total_count=len(messages)
    )


@router.delete("/history")
async def clear_chat_history(
    current_user: User = Depends(get_current_user)
):
    """
    Clear chat conversation history for the current user.
    """
    user_id = str(current_user.id)
    
    if user_id in _chat_histories:
        del _chat_histories[user_id]
    
    return {"message": "Chat history cleared successfully"}
