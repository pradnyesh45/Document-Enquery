from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.base import Base
from app.db.session import engine
from app.core.config import settings
from app.api.v1 import api_router
from fastapi.openapi.utils import get_openapi

print(f"Database URL: {settings.SQLALCHEMY_DATABASE_URI}")
print("Creating tables...")

app = FastAPI(
    title="Document Enquery API",
    openapi_url="/api/v1/openapi.json",
    docs_url="/docs",
    swagger_ui_oauth2_redirect_url="/api/v1/users/login",
    openapi_tags=[{"name": "users"}, {"name": "documents"}],
)

# Update the OpenAPI schema to use the correct token URL
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Document Enquery API",
        version="1.0.0",
        description="API for document processing and querying",
        routes=app.routes,
    )
    
    # Update the security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": "/api/v1/users/login",  # Correct token URL
                    "scopes": {}
                }
            }
        }
    }
    
    # Ensure proper content type for file uploads
    for path in openapi_schema["paths"].values():
        for operation in path.values():
            if "requestBody" in operation:
                if "multipart/form-data" in operation["requestBody"]["content"]:
                    operation["requestBody"]["required"] = True
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi  # Set the custom OpenAPI schema

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Adjust this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
Base.metadata.create_all(bind=engine)
print("Tables created!")

# Include API router
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Welcome to Document Processing API"}