from sqlalchemy.orm import Session
from app.models.chat import ChatSession, ChatMessage
from app.services.rag_agent import RAGAgent
from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException

class ChatService:
    def __init__(self, db: Session):
        self.db = db
        self.rag_agent = RAGAgent()

    async def create_session(self, user_id: UUID, document_id: UUID) -> ChatSession:
        """Create a new chat session"""
        session = ChatSession(user_id=user_id, document_id=document_id)
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    async def get_session(self, session_id: UUID, user_id: UUID) -> Optional[ChatSession]:
        """Get a chat session by ID"""
        return self.db.query(ChatSession).filter(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id
        ).first()

    async def get_user_sessions(self, user_id: UUID) -> List[ChatSession]:
        """Get all chat sessions for a user"""
        return self.db.query(ChatSession)\
            .filter(ChatSession.user_id == user_id)\
            .order_by(ChatSession.created_at.desc())\
            .all()

    async def delete_session(self, session_id: UUID, user_id: UUID) -> bool:
        """Delete a chat session"""
        session = await self.get_session(session_id, user_id)
        if not session:
            return False
        
        self.db.delete(session)
        self.db.commit()
        return True

    async def add_message(
        self, 
        session_id: UUID, 
        user_id: UUID, 
        content: str
    ) -> tuple[ChatMessage, ChatMessage]:
        """Add a user message and get AI response"""
        session = await self.get_session(session_id, user_id)
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")

        # Create user message
        user_message = ChatMessage(
            session_id=session_id,
            role="user",
            content=content
        )
        self.db.add(user_message)
        
        try:
            # Get AI response
            response = await self.rag_agent.answer_question(
                question=content,
                document_ids=[session.document_id]
            )

            # Create assistant message
            assistant_message = ChatMessage(
                session_id=session_id,
                role="assistant",
                content=response["answer"]
            )
            self.db.add(assistant_message)
            self.db.commit()
            
            return user_message, assistant_message, response["sources"]
            
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to generate response: {str(e)}"
            )

    async def get_messages(
        self, 
        session_id: UUID, 
        user_id: UUID, 
        limit: int = 50, 
        before_id: Optional[UUID] = None
    ) -> List[ChatMessage]:
        """Get messages for a chat session with pagination"""
        query = self.db.query(ChatMessage)\
            .join(ChatSession)\
            .filter(
                ChatSession.id == session_id,
                ChatSession.user_id == user_id
            )
            
        if before_id:
            query = query.filter(ChatMessage.id < before_id)
            
        return query.order_by(ChatMessage.created_at.desc())\
            .limit(limit)\
            .all() 