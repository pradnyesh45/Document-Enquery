from sqlalchemy import Column, String, DateTime, UUID, JSON, ForeignKey, Index
from sqlalchemy.dialects.postgresql import VECTOR
from sqlalchemy.sql import func
import uuid
from app.db.base import Base

class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("documents.id", ondelete="CASCADE"), 
        nullable=False
    )
    content = Column(String, nullable=False)
    metadata = Column(JSON, nullable=False, default={})
    embedding = Column(VECTOR(1536), nullable=False)  # OpenAI embeddings are 1536 dimensions
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        # Create an IVF index for faster similarity search
        Index(
            'document_chunks_embedding_idx',
            embedding,
            postgresql_using='ivfflat',
            postgresql_with={'lists': 100},
            postgresql_ops={'embedding': 'vector_cosine_ops'}
        ),
    ) 