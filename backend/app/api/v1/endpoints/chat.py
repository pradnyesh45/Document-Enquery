from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.chat import ChatService
from app.schemas.chat import (
    ChatMessageCreate, 
    ChatMessageResponse, 
    ChatSessionResponse
)
from app.api.dependencies.auth import get_current_user
from typing import List, Optional
from uuid import UUID
from app.models.user import User

router = APIRouter()

@router.post("/sessions", response_model=ChatSessionResponse)
async def create_chat_session(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new chat session for a document"""
    chat_service = ChatService(db)
    session = await chat_service.create_session(current_user.id, document_id)
    return session

@router.get("/sessions", response_model=List[ChatSessionResponse])
async def list_chat_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all chat sessions for the current user"""
    chat_service = ChatService(db)
    return await chat_service.get_user_sessions(current_user.id)

@router.delete("/sessions/{session_id}")
async def delete_chat_session(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a chat session"""
    chat_service = ChatService(db)
    success = await chat_service.delete_session(session_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return {"message": "Session deleted successfully"}

@router.post("/sessions/{session_id}/messages", response_model=ChatMessageResponse)
async def send_message(
    session_id: UUID,
    message: ChatMessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message and get AI response"""
    chat_service = ChatService(db)
    user_msg, ai_msg, sources = await chat_service.add_message(
        session_id=session_id,
        user_id=current_user.id,
        content=message.content
    )
    
    return ChatMessageResponse(
        id=ai_msg.id,
        content=ai_msg.content,
        role=ai_msg.role,
        created_at=ai_msg.created_at,
        sources=sources
    )

@router.get("/sessions/{session_id}/messages", response_model=List[ChatMessageResponse])
async def get_messages(
    session_id: UUID,
    before_id: Optional[UUID] = None,
    limit: int = Query(default=50, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get messages in a chat session with pagination"""
    chat_service = ChatService(db)
    messages = await chat_service.get_messages(
        session_id=session_id,
        user_id=current_user.id,
        limit=limit,
        before_id=before_id
    )
    return messages