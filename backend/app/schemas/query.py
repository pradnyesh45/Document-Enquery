from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional, List

class QueryCreate(BaseModel):
    document_id: UUID = Field(..., description="ID of the document to query")
    question: str = Field(..., description="Question to ask about the document")

class QueryResponse(BaseModel):
    document_id: UUID
    question: str
    answer: str
    confidence_score: Optional[float] = None
    source_documents: Optional[List[str]] = None 