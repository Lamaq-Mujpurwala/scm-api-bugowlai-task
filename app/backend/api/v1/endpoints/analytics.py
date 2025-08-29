from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.backend.database.session import get_db
from app.backend.services.analytics_service import AnalyticsService
from app.backend.schemas.analytics import AnalyticsSummary

router = APIRouter()

@router.get("/summary", response_model=AnalyticsSummary)
async def get_analytics_summary(
    user: str = Query(..., description="User email address"),
    db: Session = Depends(get_db)
):
    """
    Get analytics summary for a specific user.
    """
    try:
        analytics_service = AnalyticsService(db)
        summary = analytics_service.get_user_summary(user)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
