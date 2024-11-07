from sqlalchemy import Column, String, DateTime, UUID, BigInteger, ForeignKey, Text, Integer, JSON, ARRAY, Float
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.base import Base
from sqlalchemy.orm import relationship
from datetime import datetime

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_size = Column(BigInteger, nullable=False)
    status = Column(String, default="pending")  # pending, processing, completed, failed
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 

    # Fix the relationship name to match DocumentChunk's back_populates
    document_chunks = relationship("DocumentChunk", back_populates="document")

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"))
    content = Column(Text)
    chunk_index = Column(Integer)
    embedding = Column(ARRAY(Float))  # For vector storage
    chunk_metadata = Column(JSON)  # Changed from 'metadata' to 'chunk_metadata'
    created_at = Column(DateTime, default=datetime.utcnow)

    # This stays the same
    document = relationship("Document", back_populates="document_chunks")