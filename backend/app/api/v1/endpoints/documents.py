from fastapi import (
    APIRouter, 
    Depends, 
    HTTPException, 
    UploadFile, 
    File, 
    BackgroundTasks, 
    Form,
    status
)
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.models.document import Document
from app.schemas.document import DocumentResponse, DocumentCreate
from app.services.document import DocumentService
from app.api.dependencies.auth import get_current_user
from uuid import UUID, uuid4
from datetime import datetime
from typing import List

router = APIRouter()

@router.post("/", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a new document"""
    try:
        document_service = DocumentService(db)
        document = await document_service.create_document(
            user_id=current_user.id,
            title=title,
            file=file
        )
        
        # Make sure we return a valid DocumentResponse
        return DocumentResponse(
            id=document.id,
            title=document.title,
            created_at=document.created_at,
            status=document.status,
            file_url=document.file_url
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.post(
    "/",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload Document",
    description="Upload a new document and trigger processing",
    response_description="The created document"
)
async def upload_document(
    *,  # Force keyword arguments
    file: UploadFile = File(
        ...,
        description="The document file to upload (PDF, PPTX, XLSX, CSV)"
    ),
    title: str = Form(
        ...,
        description="Title of the document",
        example="My Important Document"
    ),
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a new document with the following steps:
    
    - Validate file size and type
    - Create document record
    - Store file in S3
    - Trigger background processing
    """
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

@router.get("/status/{document_id}", response_model=dict)
async def get_document_status(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the processing status of a document"""
    document_service = DocumentService(db)
    return await document_service.get_document_status(document_id, current_user.id)

@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all documents for the current user"""
    document_service = DocumentService(db)
    return await document_service.list_documents(current_user.id, skip, limit)

@router.delete("/{document_id}")
async def delete_document(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a document"""
    document_service = DocumentService(db)
    success = await document_service.delete_document(document_id, current_user.id)
    return {"message": "Document deleted successfully"}

@router.get("/debug/{document_id}", include_in_schema=False)
async def debug_document(
    document_id: UUID,
    db: Session = Depends(get_db)
):
    """Debug endpoint to check document details"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if document:
        return {
            "id": str(document.id),
            "user_id": str(document.user_id),
            "title": document.title,
            "status": document.status,
            "file_url": document.file_url
        }
    return {"detail": "Document not found"}

@router.get("/whoami", include_in_schema=False)
async def whoami(
    current_user: User = Depends(get_current_user)
):
    """Debug endpoint to check current user ID"""
    return {
        "user_id": str(current_user.id),
        "email": current_user.email
    }