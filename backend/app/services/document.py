from sqlalchemy.orm import Session
from fastapi import UploadFile
from app.models.document import Document
from app.schemas.document import DocumentCreate
from app.services.s3 import S3Service
from uuid import UUID
from typing import List

class DocumentService:
    def __init__(self, db: Session):
        self.db = db
        self.s3_service = S3Service()

    async def create_document(
        self, 
        user_id: UUID, 
        file: UploadFile, 
        document: DocumentCreate
    ) -> Document:
        # Upload file to S3
        file_path = await self.s3_service.upload_file(file, user_id)
        
        # Create document record
        db_document = Document(
            user_id=user_id,
            title=document.title,
            file_path=file_path,
            file_type=file.content_type,
            file_size=file.size,
            status="pending"
        )
        
        self.db.add(db_document)
        self.db.commit()
        self.db.refresh(db_document)
        
        # Here you would typically trigger async processing
        # await self.trigger_document_processing(db_document.id)
        
        return db_document

    async def get_user_documents(self, user_id: UUID) -> List[Document]:
        return self.db.query(Document)\
            .filter(Document.user_id == user_id)\
            .order_by(Document.created_at.desc())\
            .all()

    async def get_document(self, document_id: UUID, user_id: UUID) -> Document:
        return self.db.query(Document)\
            .filter(Document.id == document_id, Document.user_id == user_id)\
            .first()

    async def delete_document(self, document_id: UUID, user_id: UUID) -> bool:
        document = await self.get_document(document_id, user_id)
        if not document:
            return False
            
        # Delete from S3
        await self.s3_service.delete_file(document.file_path)
        
        # Delete from database
        self.db.delete(document)
        self.db.commit()
        
        return True 