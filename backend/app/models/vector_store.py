from sqlalchemy import Column, String, DateTime, UUID, Text, ForeignKey, Integer
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import ARRAY, FLOAT
import uuid
from app.db.base import Base

class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(ARRAY(FLOAT(precision=6)), nullable=True)
    chunk_index = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now()) 