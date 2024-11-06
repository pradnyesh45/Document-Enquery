from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.models.document import DocumentChunk
from langchain.embeddings import OpenAIEmbeddings
import numpy as np
from typing import List, Dict, Optional
import logging
from uuid import UUID

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self, db: Session):
        self.db = db
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=get_settings().OPENAI_API_KEY
        )
        
    async def create_embedding(self, text: str) -> List[float]:
        """Create embedding for a single text"""
        try:
            return await self.embeddings.embed_query(text)
        except Exception as e:
            logger.error(f"Error creating embedding: {e}")
            raise Exception(f"Failed to create embedding: {str(e)}")

    async def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for multiple texts"""
        try:
            return await self.embeddings.embed_documents(texts)
        except Exception as e:
            logger.error(f"Error creating embeddings: {e}")
            raise Exception(f"Failed to create embeddings: {str(e)}")

    async def store_document_chunks(
        self, 
        document_id: UUID, 
        chunks: List[Dict]
    ) -> None:
        """Store document chunks with their embeddings"""
        try:
            # Create embeddings for all chunks
            texts = [chunk['content'] for chunk in chunks]
            embeddings = await self.create_embeddings(texts)
            
            # Store chunks and embeddings
            for chunk, embedding in zip(chunks, embeddings):
                db_chunk = DocumentChunk(
                    document_id=document_id,
                    content=chunk['content'],
                    metadata=chunk.get('metadata', {}),
                    embedding=embedding
                )
                self.db.add(db_chunk)
            
            self.db.commit()
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error storing document chunks: {e}")
            raise Exception(f"Failed to store document chunks: {str(e)}")

    async def similarity_search(
        self,
        query: str,
        document_ids: List[UUID],
        limit: int = 3,
        similarity_threshold: float = 0.7
    ) -> List[Dict]:
        """
        Perform similarity search against stored document chunks
        """
        try:
            # Create query embedding
            query_embedding = await self.create_embedding(query)
            
            # Convert document_ids to strings for SQL
            doc_ids_str = ",".join([f"'{id}'" for id in document_ids])
            
            # Perform similarity search using cosine similarity
            sql_query = text("""
                SELECT 
                    content,
                    metadata,
                    1 - (embedding <-> :query_embedding) as similarity
                FROM document_chunks
                WHERE document_id = ANY(:document_ids)
                AND 1 - (embedding <-> :query_embedding) > :similarity_threshold
                ORDER BY embedding <-> :query_embedding
                LIMIT :limit
            """)
            
            result = self.db.execute(
                sql_query,
                {
                    "query_embedding": query_embedding,
                    "document_ids": document_ids,
                    "similarity_threshold": similarity_threshold,
                    "limit": limit
                }
            )
            
            matches = []
            for row in result:
                matches.append({
                    "content": row.content,
                    "metadata": row.metadata,
                    "score": float(row.similarity)
                })
            
            return matches
            
        except Exception as e:
            logger.error(f"Error performing similarity search: {e}")
            raise Exception(f"Failed to perform similarity search: {str(e)}")

    async def delete_document_chunks(self, document_id: UUID) -> None:
        """Delete all chunks for a document"""
        try:
            self.db.query(DocumentChunk)\
                .filter(DocumentChunk.document_id == document_id)\
                .delete()
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting document chunks: {e}")
            raise Exception(f"Failed to delete document chunks: {str(e)}")

    async def get_document_chunks(
        self,
        document_id: UUID,
        offset: int = 0,
        limit: int = 100
    ) -> List[Dict]:
        """Get chunks for a document with pagination"""
        try:
            chunks = self.db.query(DocumentChunk)\
                .filter(DocumentChunk.document_id == document_id)\
                .offset(offset)\
                .limit(limit)\
                .all()
                
            return [
                {
                    "content": chunk.content,
                    "metadata": chunk.metadata,
                    "created_at": chunk.created_at
                }
                for chunk in chunks
            ]
        except Exception as e:
            logger.error(f"Error getting document chunks: {e}")
            raise Exception(f"Failed to get document chunks: {str(e)}")