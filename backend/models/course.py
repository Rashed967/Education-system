from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum
import uuid

class CourseType(str, Enum):
    FREE = "free"
    PAID = "paid"

class Lesson(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    video_url: str  # YouTube/Vimeo URL
    video_type: str  # "youtube" or "vimeo"
    duration: Optional[int] = None  # in minutes
    order: int
    is_preview: bool = False  # First lesson should be preview
    resources: List[str] = []  # Additional resources/attachments

class LessonCreate(BaseModel):
    title: str
    description: str
    video_url: str
    video_type: str
    duration: Optional[int] = None
    is_preview: bool = False
    resources: List[str] = []

class Course(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    instructor_name: str
    instructor_id: Optional[str] = None
    course_type: CourseType
    price: Optional[float] = None  # BDT
    thumbnail_url: Optional[str] = None
    lessons: List[Lesson] = []
    total_duration: Optional[int] = None  # in minutes
    student_count: int = 0
    rating: Optional[float] = None
    rating_count: int = 0
    category: Optional[str] = None
    tags: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

class CourseCreate(BaseModel):
    title: str
    description: str
    instructor_name: str
    course_type: CourseType
    price: Optional[float] = None
    thumbnail_url: Optional[str] = None
    category: Optional[str] = None
    tags: List[str] = []