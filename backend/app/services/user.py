from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash
from app.db import SessionLocal

class UserService:
    async def create_user(self, user: UserCreate) -> User:
        db = SessionLocal()
        try:
            db_user = User(
                email=user.email,
                hashed_password=get_password_hash(user.password)
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            return db_user
        finally:
            db.close()

    async def get_user_by_email(self, email: str) -> User | None:
        db = SessionLocal()
        try:
            return db.query(User).filter(User.email == email).first()
        finally:
            db.close() 