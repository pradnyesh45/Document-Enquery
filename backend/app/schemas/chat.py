from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import List, Optional, Dict

class ChatMessageCreate(BaseModel):
    content: str

class Source(BaseModel):
    content: str
    metadata: Dict
    score: float

class ChatMessageResponse(BaseModel):
    id: UUID
    content: str
    role: str
    created_at: datetime
    sources: Optional[List[Source]]

class ChatSessionResponse(BaseModel):
    id: UUID
    document_id: UUID
    created_at: datetime
    messages: List[ChatMessageResponse] 