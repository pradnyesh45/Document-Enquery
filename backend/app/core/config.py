from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str = "Document Processing API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "pradnyeshaglawe"  # Your actual username
    POSTGRES_PASSWORD: str = ""  # Empty string since no password is needed
    POSTGRES_DB: str = "document_enquery"
    POSTGRES_PORT: str = "5432"
    
    @property
    def DATABASE_URL(self) -> str:
        # Simple URL without password since none is needed
        return f"postgresql://{self.POSTGRES_USER}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # AWS
    AWS_ACCESS_KEY_ID: str = "your-access-key"
    AWS_SECRET_ACCESS_KEY: str = "your-secret-key"
    S3_BUCKET_NAME: str = "your-bucket-name"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Google API Key
    GOOGLE_API_KEY: str
    
    class Config:
        case_sensitive = True
        env_file = ".env"

@lru_cache
def get_settings():
    return Settings()

settings = Settings() 