from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Dict, List
from datetime import datetime, timedelta

from app.backend.models.moderation import ModerationRequest, ModerationResult, ContentStatus, Classification
from app.backend.schemas.analytics import AnalyticsSummary

class AnalyticsService:
    """Service for analytics and reporting"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_summary(self, user_email: str) -> AnalyticsSummary:
        """Get analytics summary for a specific user"""
        # Get all requests for the user
        requests = self.db.query(ModerationRequest).filter(
            ModerationRequest.user_email == user_email
        ).all()
        
        if not requests:
            return AnalyticsSummary(
                user_email=user_email,
                total_requests=0,
                completed_requests=0,
                failed_requests=0,
                classification_breakdown={},
                recent_activity=[],
                last_request_date=None
            )
        
        # Calculate basic metrics
        total_requests = len(requests)
        completed_requests = len([r for r in requests if r.status == ContentStatus.COMPLETED])
        failed_requests = len([r for r in requests if r.status == ContentStatus.FAILED])
        
        # Get classification breakdown
        classification_breakdown = {}
        for request in requests:
            if request.status == ContentStatus.COMPLETED and request.result:
                classification = request.result.classification.value
                classification_breakdown[classification] = classification_breakdown.get(classification, 0) + 1
        
        # Get recent activity (last 10 requests)
        recent_activity = []
        recent_requests = self.db.query(ModerationRequest).filter(
            ModerationRequest.user_email == user_email
        ).order_by(desc(ModerationRequest.created_at)).limit(10).all()
        
        for request in recent_requests:
            activity_item = {
                "request_id": request.id,
                "content_type": request.content_type,
                "status": request.status.value,
                "created_at": request.created_at.isoformat() if request.created_at else None
            }
            
            if request.result:
                activity_item.update({
                    "classification": request.result.classification.value,
                    "confidence": request.result.confidence,
                    "llm_provider": request.result.llm_provider
                })
            
            recent_activity.append(activity_item)
        
        # Get last request date
        last_request = self.db.query(ModerationRequest).filter(
            ModerationRequest.user_email == user_email
        ).order_by(desc(ModerationRequest.created_at)).first()
        
        last_request_date = last_request.created_at if last_request else None
        
        return AnalyticsSummary(
            user_email=user_email,
            total_requests=total_requests,
            completed_requests=completed_requests,
            failed_requests=failed_requests,
            classification_breakdown=classification_breakdown,
            recent_activity=recent_activity,
            last_request_date=last_request_date
        )
    
    def get_system_summary(self) -> Dict:
        """Get system-wide analytics summary"""
        # Total requests
        total_requests = self.db.query(ModerationRequest).count()
        
        # Requests by status
        status_counts = self.db.query(
            ModerationRequest.status,
            func.count(ModerationRequest.id)
        ).group_by(ModerationRequest.status).all()
        
        # Classification breakdown
        classification_counts = self.db.query(
            ModerationResult.classification,
            func.count(ModerationResult.id)
        ).group_by(ModerationResult.classification).all()
        
        # Recent activity (last 24 hours)
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_requests = self.db.query(ModerationRequest).filter(
            ModerationRequest.created_at >= yesterday
        ).count()
        
        return {
            "total_requests": total_requests,
            "status_breakdown": {status.value: count for status, count in status_counts},
            "classification_breakdown": {cls.value: count for cls, count in classification_counts},
            "recent_requests_24h": recent_requests
        }
