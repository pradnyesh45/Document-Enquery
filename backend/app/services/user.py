from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash

class UserService:
    def __init__(self, db: Session):
        self.db = db

    async def create_user(self, user: UserCreate) -> User:
        # Check if user exists
        db_user = self.db.query(User).filter(User.email == user.email).first()
        if db_user:
            raise ValueError("Email already registered")
            
        # Create new user
        db_user = User(
            email=user.email,
            password_hash=get_password_hash(user.password)
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user 