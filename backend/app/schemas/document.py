from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from typing import Optional

class DocumentBase(BaseModel):
    title: str = Field(..., description="Title of the document")

class DocumentCreate(DocumentBase):
    pass

class DocumentResponse(DocumentBase):
    id: UUID = Field(..., description="Unique identifier")
    created_at: datetime = Field(..., description="When the document was created")
    status: str = Field(..., description="Processing status")
    file_url: Optional[str] = Field(None, description="URL to access the file")

    class Config:
        from_attributes = True