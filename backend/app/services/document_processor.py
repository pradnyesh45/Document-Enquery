from unstructured.partition.auto import partition
from unstructured.partition.pdf import partition_pdf
from unstructured.partition.pptx import partition_pptx
from unstructured.partition.xlsx import partition_xlsx
from unstructured.staging.base import elements_to_json
from unstructured.cleaners.core import clean_extra_whitespace
from app.services.vector_store import VectorStore
from app.services.s3 import S3Service
from app.models.document import Document
from sqlalchemy.orm import Session
import tempfile
import os
import logging
from typing import List, Dict
import asyncio
from fastapi import BackgroundTasks
from uuid import UUID

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self, db: Session):
        self.db = db
        self.vector_store = VectorStore(db)
        self.s3_service = S3Service()
        
    async def process_file_content(self, file_path: str, file_type: str) -> List[Dict]:
        """Process different file types and extract structured content"""
        try:
            if file_type == "application/pdf":
                elements = partition_pdf(file_path)
            elif file_type in ["application/vnd.ms-powerpoint", "application/vnd.openxmlformats-officedocument.presentationml.presentation"]:
                elements = partition_pptx(file_path)
            elif file_type in ["application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]:
                elements = partition_xlsx(file_path)
            else:
                elements = partition(filename=file_path)

            # Clean and structure the elements
            cleaned_elements = []
            for element in elements:
                # Clean the text
                cleaned_text = clean_extra_whitespace(str(element))
                
                # Create structured element
                cleaned_element = {
                    "text": cleaned_text,
                    "type": element.category,
                    "metadata": {
                        "page_number": getattr(element, "page_number", None),
                        "coordinates": getattr(element, "coordinates", None)
                    }
                }
                cleaned_elements.append(cleaned_element)

            return cleaned_elements

        except Exception as e:
            logger.error(f"Error processing file content: {str(e)}")
            raise Exception(f"Failed to process document: {str(e)}")

    async def prepare_chunks(self, elements: List[Dict]) -> List[str]:
        """Prepare document chunks from processed elements"""
        chunks = []
        current_chunk = ""
        
        for element in elements:
            # Skip empty or irrelevant elements
            if not element["text"].strip():
                continue
                
            # Add page number context if available
            page_info = f" [Page {element['metadata']['page_number']}] " if element['metadata']['page_number'] else " "
            
            # Combine elements into chunks
            if len(current_chunk) + len(element["text"]) < 1000:
                current_chunk += element["text"] + page_info
            else:
                chunks.append(current_chunk)
                current_chunk = element["text"] + page_info
        
        # Add the last chunk if not empty
        if current_chunk:
            chunks.append(current_chunk)
            
        return chunks

    async def process_document(self, document_id: UUID) -> None:
        """Main document processing function"""
        try:
            # Get document from database
            document = self.db.query(Document).filter(Document.id == document_id).first()
            if not document:
                raise Exception("Document not found")

            # Update status to processing
            document.status = "processing"
            self.db.commit()

            # Download file from S3 to temp location
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                await self.s3_service.download_file(document.file_path, temp_file.name)
                
                try:
                    # Process the document
                    elements = await self.process_file_content(temp_file.name, document.file_type)
                    
                    # Prepare chunks
                    chunks = await self.prepare_chunks(elements)
                    
                    # Prepare chunks with metadata
                    processed_chunks = []
                    processed_metadata = []
                    for idx, content in enumerate(chunks):
                        processed_chunk = {
                            "content": content,
                            "metadata": {
                                "chunk_index": idx,
                                "document_id": str(document_id),
                                "page_number": elements[idx]['metadata'].get("page_number"),
                                # Add other relevant metadata
                            }
                        }
                        processed_chunks.append(processed_chunk)
                        processed_metadata.append(elements[idx]['metadata'])

                    # Store chunks with embeddings
                    await self.vector_store.store_document_chunks(document_id, processed_chunks)

                    # Update document status
                    document.status = "completed"
                    self.db.commit()
                    
                except Exception as e:
                    document.status = "failed"
                    document.error_message = str(e)
                    self.db.commit()
                    raise e
                    
                finally:
                    # Clean up temp file
                    os.unlink(temp_file.name)

        except Exception as e:
            logger.error(f"Error processing document {document_id}: {str(e)}")
            document.status = "failed"
            document.error_message = str(e)
            self.db.commit()
            raise e