from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid

class Enrollment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    course_id: str
    enrolled_at: datetime = Field(default_factory=datetime.utcnow)
    payment_status: str = "pending"  # pending, completed, failed
    transaction_id: Optional[str] = None
    payment_method: Optional[str] = None  # bkash, nagad, card, etc.
    progress: float = 0.0  # 0-100 percentage
    completed_lessons: List[str] = []
    last_accessed_at: Optional[datetime] = None