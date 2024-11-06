from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional

class DocumentBase(BaseModel):
    title: str

class DocumentCreate(DocumentBase):
    pass

class DocumentResponse(DocumentBase):
    id: UUID
    user_id: UUID
    file_path: str
    file_type: str
    file_size: int
    status: str
    error_message: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True 