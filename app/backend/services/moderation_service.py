import hashlib
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from datetime import datetime

from app.backend.models.moderation import ModerationRequest, ModerationResult, NotificationLog, ContentStatus, Classification
from app.backend.services.llm_service import LLMService
from app.backend.services.notification_service import NotificationService
from app.backend.schemas.moderation import ModerationResponse, ModerationResultResponse

class ModerationService:
    """Main service for content moderation operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.llm_service = LLMService()
        self.notification_service = NotificationService()
    
    def _generate_content_hash(self, content: str) -> str:
        """Generate a hash for content to prevent duplicates"""
        return hashlib.sha256(content.encode()).hexdigest()
    
    async def moderate_text(
        self, 
        user_email: str, 
        text_content: str,
        llm_provider: str = None
    ) -> ModerationResponse:
        """Moderate text content"""
        # Generate content hash
        content_hash = self._generate_content_hash(text_content)
        
        # Check for existing request
        existing_request = self.db.query(ModerationRequest).filter(
            ModerationRequest.content_hash == content_hash
        ).first()
        
        if existing_request:
            return ModerationResponse(
                request_id=existing_request.id,
                user_email=existing_request.user_email,
                content_type=existing_request.content_type,
                status=existing_request.status,
                created_at=existing_request.created_at
            )
        
        # Create new moderation request
        db_request = ModerationRequest(
            user_email=user_email,
            content_type="text",
            content_hash=content_hash,
            status=ContentStatus.PENDING
        )
        self.db.add(db_request)
        self.db.commit()
        self.db.refresh(db_request)
        
        try:
            # Analyze content with LLM
            llm_result = await self.llm_service.analyze_text(text_content, llm_provider)
            
            # Create moderation result
            db_result = ModerationResult(
                request_id=db_request.id,
                classification=Classification(llm_result["classification"]),
                confidence=llm_result.get("confidence", 0.0),
                reasoning=llm_result.get("reasoning", ""),
                llm_provider=llm_result.get("llm_provider", "unknown"),
                llm_response=llm_result
            )
            self.db.add(db_result)
            
            # Update request status
            db_request.status = ContentStatus.COMPLETED
            self.db.commit()
            
            # Send notifications if content is flagged
            if llm_result["classification"] in ["toxic", "spam", "harassment"]:
                await self._send_notifications(
                    db_request.id,
                    user_email,
                    llm_result["classification"],
                    "text",
                    llm_result.get("confidence", 0.0),
                    llm_result.get("reasoning", "")
                )
            
            return ModerationResponse(
                request_id=db_request.id,
                user_email=db_request.user_email,
                content_type=db_request.content_type,
                status=db_request.status,
                created_at=db_request.created_at
            )
            
        except Exception as e:
            # Update request status to failed
            db_request.status = ContentStatus.FAILED
            self.db.commit()
            raise e
    
    async def moderate_image(
        self, 
        user_email: str, 
        image_data: str,
        llm_provider: str = None
    ) -> ModerationResponse:
        """Moderate image content"""
        # Generate content hash
        content_hash = self._generate_content_hash(image_data)
        
        # Check for existing request
        existing_request = self.db.query(ModerationRequest).filter(
            ModerationRequest.content_hash == content_hash
        ).first()
        
        if existing_request:
            return ModerationResponse(
                request_id=existing_request.id,
                user_email=existing_request.user_email,
                content_type=existing_request.content_type,
                status=existing_request.status,
                created_at=existing_request.created_at
            )
        
        # Create new moderation request
        db_request = ModerationRequest(
            user_email=user_email,
            content_type="image",
            content_hash=content_hash,
            status=ContentStatus.PENDING
        )
        self.db.add(db_request)
        self.db.commit()
        self.db.refresh(db_request)
        
        try:
            # Analyze content with LLM
            llm_result = await self.llm_service.analyze_image(image_data, llm_provider)
            
            # Create moderation result
            db_result = ModerationResult(
                request_id=db_request.id,
                classification=Classification(llm_result["classification"]),
                confidence=llm_result.get("confidence", 0.0),
                reasoning=llm_result.get("reasoning", ""),
                llm_provider=llm_result.get("llm_provider", "unknown"),
                llm_response=llm_result
            )
            self.db.add(db_result)
            
            # Update request status
            db_request.status = ContentStatus.COMPLETED
            self.db.commit()
            
            # Send notifications if content is flagged
            if llm_result["classification"] in ["toxic", "spam", "harassment"]:
                await self._send_notifications(
                    db_request.id,
                    user_email,
                    llm_result["classification"],
                    "image",
                    llm_result.get("confidence", 0.0),
                    llm_result.get("reasoning", "")
                )
            
            return ModerationResponse(
                request_id=db_request.id,
                user_email=db_request.user_email,
                content_type=db_request.content_type,
                status=db_request.status,
                created_at=db_request.created_at
            )
            
        except Exception as e:
            # Update request status to failed
            db_request.status = ContentStatus.FAILED
            self.db.commit()
            raise e
    
    def get_result(self, request_id: int) -> Optional[ModerationResultResponse]:
        """Get moderation result by request ID"""
        result = self.db.query(ModerationResult).filter(
            ModerationResult.request_id == request_id
        ).first()
        
        if not result:
            return None
            
        return ModerationResultResponse(
            request_id=result.request_id,
            classification=result.classification,
            confidence=result.confidence,
            reasoning=result.reasoning,
            llm_provider=result.llm_provider,
            created_at=result.request.created_at
        )
    
    async def _send_notifications(
        self,
        request_id: int,
        user_email: str,
        classification: str,
        content_type: str,
        confidence: float,
        reasoning: str
    ):
        """Send notifications for flagged content"""
        notification_results = await self.notification_service.send_moderation_alert(
            user_email=user_email,
            classification=classification,
            content_type=content_type,
            confidence=confidence,
            reasoning=reasoning
        )
        
        # Log notification attempts
        for channel, result in notification_results.items():
            notification_log = NotificationLog(
                request_id=request_id,
                channel=channel,
                status=result["status"]
            )
            self.db.add(notification_log)
        
        self.db.commit()
