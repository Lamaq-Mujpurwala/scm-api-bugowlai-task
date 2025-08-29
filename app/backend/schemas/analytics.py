from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime

class AnalyticsSummary(BaseModel):
    user_email: str
    total_requests: int
    completed_requests: int
    failed_requests: int
    classification_breakdown: Dict[str, int]
    recent_activity: List[Dict]
    last_request_date: Optional[datetime]
    
    class Config:
        from_attributes = True
