from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.document import DocumentCreate, DocumentResponse
from app.services.document import DocumentService
from app.services.document_processor import DocumentProcessor
from app.api.dependencies.auth import get_current_user
from typing import List
from uuid import UUID
from app.models.user import User

router = APIRouter()

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    title: str,
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a new document and trigger processing"""
    # Validate file size (example: 10MB limit)
    if file.size > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large")
        
    # Validate file type
    allowed_types = [
        "application/pdf",
        "application/vnd.ms-powerpoint",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "text/csv"
    ]
    
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="File type not supported")
    
    document_service = DocumentService(db)
    try:
        # Create document record
        document = await document_service.create_document(
            user_id=current_user.id,
            file=file,
            document=DocumentCreate(title=title)
        )
        
        # Trigger background processing
        document_processor = DocumentProcessor(db)
        background_tasks.add_task(
            document_processor.process_document,
            document.id
        )
        
        return document
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{document_id}", response_model=DocumentResponse)
async def get_document_status(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get document processing status"""
    document_service = DocumentService(db)
    document = await document_service.get_document(document_id, current_user.id)
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
        
    return document