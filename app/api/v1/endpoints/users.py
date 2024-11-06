from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.user import UserCreate, User
from app.services.user import UserService

router = APIRouter()

@router.post("/", response_model=User)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    user_service = UserService(db)
    try:
        return await user_service.create_user(user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) 