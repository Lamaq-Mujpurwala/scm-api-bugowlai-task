import enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

# Import the shared Base from the database module
from app.backend.database.base import Base

class ContentStatus(enum.Enum):
    """Enumeration for the status of a moderation request."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

class NotificationChannel(enum.Enum):
    """Enumeration for the notification channel used."""
    SLACK = "slack"
    EMAIL = "email"

class Classification(enum.Enum):
    """Enumeration for the standardized classification labels."""
    TOXIC = "toxic"
    SPAM = "spam"
    HARASSMENT = "harassment"
    SAFE = "safe"

class ModerationRequest(Base):
    """
    Represents a request to moderate a piece of content.
    This table stores the initial submission from the user.
    """
    __tablename__ = "moderation_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, nullable=False, index=True)
    content_type = Column(String, nullable=False) # e.g., 'text' or 'image'
    content_hash = Column(String, nullable=False, unique=True, index=True)
    status = Column(Enum(ContentStatus), default=ContentStatus.PENDING, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    result = relationship("ModerationResult", back_populates="request", uselist=False)
    notification_logs = relationship("NotificationLog", back_populates="request")

class ModerationResult(Base):
    """
    Stores the result of the content moderation analysis from the LLM.
    This is linked to a specific ModerationRequest.
    """
    __tablename__ = "moderation_results"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("moderation_requests.id"), nullable=False, index=True)
    classification = Column(Enum(Classification), nullable=False)
    confidence = Column(Float) # Using Float for more precise scoring
    reasoning = Column(String) # Explanation from the LLM
    llm_provider = Column(String, nullable=True) # e.g., 'openai', 'gemini'
    llm_response = Column(JSONB) # The full, raw JSON response from the LLM API

    request = relationship("ModerationRequest", back_populates="result")

class NotificationLog(Base):
    """
    Logs every attempt to send a notification for a moderation result.
    This helps in auditing and debugging notification failures.
    """
    __tablename__ = "notification_logs"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("moderation_requests.id"), nullable=False, index=True)
    channel = Column(Enum(NotificationChannel), nullable=False) # 'slack' or 'email'
    status = Column(String, nullable=False) # e.g., 'success', 'failed'
    sent_at = Column(DateTime(timezone=True), server_default=func.now())

    request = relationship("ModerationRequest", back_populates="notification_logs")
