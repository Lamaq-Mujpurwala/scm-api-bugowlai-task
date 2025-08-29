from fastapi import APIRouter
from app.backend.api.v1.endpoints import moderation, analytics

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    moderation.router,
    prefix="/moderate",
    tags=["moderation"]
)

api_router.include_router(
    analytics.router,
    prefix="/analytics",
    tags=["analytics"]
)
