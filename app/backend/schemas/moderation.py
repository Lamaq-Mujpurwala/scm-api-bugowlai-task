from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class ContentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

class Classification(str, Enum):
    TOXIC = "toxic"
    SPAM = "spam"
    HARASSMENT = "harassment"
    SAFE = "safe"

class TextModerationRequest(BaseModel):
    user_email: str = Field(..., description="User's email address")
    text_content: str = Field(..., description="Text content to moderate")

class ImageModerationRequest(BaseModel):
    user_email: str = Field(..., description="User's email address")
    image_data: str = Field(..., description="Base64 encoded image data")

class ModerationResponse(BaseModel):
    request_id: int
    user_email: str
    content_type: str
    status: ContentStatus
    created_at: datetime
    
    class Config:
        from_attributes = True

class ModerationResultResponse(BaseModel):
    request_id: int
    classification: Classification
    confidence: Optional[float]
    reasoning: Optional[str]
    llm_provider: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
