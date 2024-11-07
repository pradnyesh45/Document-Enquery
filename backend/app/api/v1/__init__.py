from fastapi import APIRouter
from app.api.v1.endpoints import users
from app.api.v1.endpoints import documents

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])