from sqlalchemy.orm import Session
from app.models.document import Document
from app.services.s3 import S3Service
from fastapi import UploadFile, HTTPException
from uuid import UUID, uuid4
from datetime import datetime
import os

class DocumentService:
    def __init__(self, db: Session):
        self.db = db
        self.s3 = S3Service()

    async def create_document(
        self,
        user_id: UUID,
        title: str,
        file: UploadFile
    ) -> Document:
        """Create a new document record and upload file to S3"""
        
        # Create document record
        document = Document(
            id=uuid4(),
            title=title,
            user_id=user_id,
            status="processing",
            created_at=datetime.utcnow()
        )
        
        try:
            # Get original file extension
            _, file_extension = os.path.splitext(file.filename)
            
            # Create a unique file name
            file_key = f"documents/{document.id}/document{file_extension}"
            
            # Upload to S3
            file_url = await self.s3.upload_file(
                file_data=file.file,
                file_name=file_key
            )
            
            # Update document with file URL
            document.file_url = file_url
            
            # Save to database
            self.db.add(document)
            self.db.commit()
            self.db.refresh(document)
            
            return document
            
        except Exception as e:
            self.db.rollback()
            raise e

    async def get_document(self, document_id: UUID, user_id: UUID) -> Document:
        """Get a document by ID and verify ownership"""
        document = self.db.query(Document).filter(
            Document.id == document_id,
            Document.user_id == user_id
        ).first()
        
        if not document:
            raise HTTPException(
                status_code=404,
                detail="Document not found or you don't have permission to access it"
            )
        
        return document

    async def get_document_status(self, document_id: UUID, user_id: UUID) -> dict:
        """Get the processing status of a document"""
        # Add some debug logging
        print(f"Checking status for document {document_id} by user {user_id}")
        
        document = self.db.query(Document).filter(
            Document.id == document_id,
            Document.user_id == user_id
        ).first()
        
        if not document:
            raise HTTPException(
                status_code=404,
                detail="Document not found or you don't have permission to access it"
            )
        
        return {
            "id": str(document.id),
            "status": document.status,
            "created_at": document.created_at,
            "file_url": document.file_url,
            "title": document.title
        }

    async def list_documents(self, user_id: UUID, skip: int = 0, limit: int = 10) -> list[Document]:
        """List all documents for a user"""
        documents = self.db.query(Document).filter(
            Document.user_id == user_id
        ).offset(skip).limit(limit).all()
        
        return documents

    async def delete_document(self, document_id: UUID, user_id: UUID) -> bool:
        """Delete a document and its associated file"""
        document = await self.get_document(document_id, user_id)
        
        try:
            # Delete from S3 if file exists
            if document.file_url:
                file_key = document.file_url.split(f"{self.s3.bucket_name}.s3.amazonaws.com/")[1]
                await self.s3.delete_file(file_key)
            
            # Delete from database
            self.db.delete(document)
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete document: {str(e)}"
            )