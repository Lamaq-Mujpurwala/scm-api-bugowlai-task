from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

# Import database and models
from app.backend.database.base import Base
from app.backend.database.session import engine

# Import API router
from app.backend.api.v1.router import api_router
from app.backend.api.v2.router import api_router_v2

# Create FastAPI app
app = FastAPI(
    title="SCM API - Content Moderation Service",
    description="A content moderation API using LLMs",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup - create tables if using SQLite
USE_SQLITE = os.getenv("USE_SQLITE", "false").lower() == "true"
if USE_SQLITE:
    # Import models to ensure they are registered
    from app.backend.models.moderation import ModerationRequest, ModerationResult, NotificationLog
    # Create all tables automatically for SQLite
    Base.metadata.create_all(bind=engine)

# Include API routes
app.include_router(api_router, prefix="/api/v1")
app.include_router(api_router_v2, prefix="/api/v2")

@app.get("/")
async def root():
    return {"message": "SCM API - Content Moderation Service", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "connected"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
