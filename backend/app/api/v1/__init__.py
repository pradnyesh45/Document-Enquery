from fastapi import APIRouter
from app.api.v1.endpoints import documents, users

api_router = APIRouter()
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(users.router, prefix="/users", tags=["users"]) 