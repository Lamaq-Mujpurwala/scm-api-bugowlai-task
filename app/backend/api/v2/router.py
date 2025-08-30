from fastapi import APIRouter
from app.backend.api.v1.endpoints import moderation, analytics

api_router_v2 = APIRouter()

# v2 re-exports v1 endpoints for parity, but documents deployment-focused behavior
api_router_v2.include_router(moderation.router, prefix="/moderate", tags=["moderation", "v2"])
api_router_v2.include_router(analytics.router, prefix="/analytics", tags=["analytics", "v2"])
