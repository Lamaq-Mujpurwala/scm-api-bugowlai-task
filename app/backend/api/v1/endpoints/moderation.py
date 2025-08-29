from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import base64
import hashlib

from app.backend.database.session import get_db
from app.backend.services.moderation_service import ModerationService
from app.backend.schemas.moderation import (
    TextModerationRequest,
    ModerationResponse,
    ModerationResultResponse
)
from app.backend.schemas.analytics import AnalyticsSummary

router = APIRouter()

@router.post("/text", response_model=ModerationResponse)
async def moderate_text(
    request: TextModerationRequest,
    db: Session = Depends(get_db)
):
    """
    Moderate text content using LLM analysis.
    """
    try:
        moderation_service = ModerationService(db)
        result = await moderation_service.moderate_text(
            user_email=request.user_email,
            text_content=request.text_content
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/image", response_model=ModerationResponse)
async def moderate_image(
    user_email: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Moderate image content using LLM analysis.
    """
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read and encode image data
        image_data = await file.read()
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        moderation_service = ModerationService(db)
        result = await moderation_service.moderate_image(
            user_email=user_email,
            image_data=image_base64
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/results/{request_id}", response_model=ModerationResultResponse)
async def get_moderation_result(
    request_id: int,
    db: Session = Depends(get_db)
):
    """
    Get moderation result by request ID.
    """
    try:
        moderation_service = ModerationService(db)
        result = moderation_service.get_result(request_id)
        if not result:
            raise HTTPException(status_code=404, detail="Moderation result not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
