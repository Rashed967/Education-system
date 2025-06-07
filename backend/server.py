import os
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import motor.motor_asyncio
import uvicorn
from datetime import datetime, timedelta
import jwt
import hashlib
import uuid
from enum import Enum

# Environment variables
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key-change-in-production')

# MongoDB setup
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
db = client.islamic_institute

app = FastAPI(title="Islamic Institute Course Platform API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

class UserRole(str, Enum):
    STUDENT = "student"
    INSTRUCTOR = "instructor"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"

class CourseType(str, Enum):
    FREE = "free"
    PAID = "paid"

# Pydantic Models
class UserRegister(BaseModel):
    full_name: str
    email: str
    password: str
    phone: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    full_name: str
    email: str
    role: UserRole = UserRole.STUDENT
    phone: Optional[str] = None
    enrolled_courses: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

class Lesson(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    video_url: str  # YouTube/Vimeo URL
    video_type: str  # "youtube" or "vimeo"
    duration: Optional[int] = None  # in minutes
    order: int
    is_preview: bool = False  # First lesson should be preview

class Course(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    instructor_name: str
    course_type: CourseType
    price: Optional[float] = None  # BDT
    thumbnail_url: Optional[str] = None
    lessons: List[Lesson] = []
    total_duration: Optional[int] = None  # in minutes
    student_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

class CourseCreate(BaseModel):
    title: str
    description: str
    instructor_name: str
    course_type: CourseType
    price: Optional[float] = None
    thumbnail_url: Optional[str] = None

class LessonCreate(BaseModel):
    title: str
    description: str
    video_url: str
    video_type: str
    duration: Optional[int] = None
    is_preview: bool = False

class Enrollment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    course_id: str
    enrolled_at: datetime = Field(default_factory=datetime.utcnow)
    payment_status: str = "pending"  # pending, completed, failed
    transaction_id: Optional[str] = None

# Utility Functions
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm="HS256")
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=["HS256"])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = await db.users.find_one({"email": email})
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# API Routes

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "Islamic Institute Course Platform API"}

# Authentication Routes
@app.post("/api/auth/register")
async def register_user(user_data: UserRegister):
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        phone=user_data.phone
    )
    
    # Hash password and store separately
    user_dict = user.dict()
    user_dict["password"] = hash_password(user_data.password)
    
    await db.users.insert_one(user_dict)
    
    # Create access token
    access_token = create_access_token(data={"sub": user.email})
    
    return {
        "message": "User registered successfully",
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role
        }
    }

@app.post("/api/auth/login")
async def login_user(login_data: UserLogin):
    user = await db.users.find_one({"email": login_data.email})
    if not user or not verify_password(login_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not user.get("is_active", True):
        raise HTTPException(status_code=401, detail="Account is disabled")
    
    access_token = create_access_token(data={"sub": user["email"]})
    
    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "full_name": user["full_name"],
            "email": user["email"],
            "role": user["role"]
        }
    }

@app.get("/api/auth/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    return {
        "id": current_user["id"],
        "full_name": current_user["full_name"],
        "email": current_user["email"],
        "role": current_user["role"],
        "enrolled_courses": current_user.get("enrolled_courses", [])
    }

# Course Routes
@app.get("/api/courses")
async def get_courses():
    courses = await db.courses.find({"is_active": True}).to_list(None)
    # Convert MongoDB ObjectId to string
    for course in courses:
        if '_id' in course:
            course['_id'] = str(course['_id'])
    return {"courses": courses}

@app.get("/api/courses/{course_id}")
async def get_course(course_id: str, current_user: dict = Depends(get_current_user)):
    course = await db.courses.find_one({"id": course_id, "is_active": True})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Check if user is enrolled
    is_enrolled = course_id in current_user.get("enrolled_courses", [])
    
    # If not enrolled and course is paid, only show preview lessons
    if not is_enrolled and course["course_type"] == "paid":
        course["lessons"] = [lesson for lesson in course.get("lessons", []) if lesson.get("is_preview", False)]
    
    course["is_enrolled"] = is_enrolled
    return course

@app.post("/api/courses")
async def create_course(course_data: CourseCreate, current_user: dict = Depends(get_current_user)):
    # Check if user is admin or instructor
    if current_user["role"] not in ["admin", "super_admin", "instructor"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    course = Course(**course_data.dict())
    course_dict = course.dict()
    
    await db.courses.insert_one(course_dict)
    return {"message": "Course created successfully", "course_id": course.id}

@app.post("/api/courses/{course_id}/lessons")
async def add_lesson_to_course(course_id: str, lesson_data: LessonCreate, current_user: dict = Depends(get_current_user)):
    # Check permissions
    if current_user["role"] not in ["admin", "super_admin", "instructor"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    course = await db.courses.find_one({"id": course_id})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Create lesson
    lesson = Lesson(**lesson_data.dict())
    lesson.order = len(course.get("lessons", [])) + 1
    
    # Update course with new lesson
    await db.courses.update_one(
        {"id": course_id},
        {"$push": {"lessons": lesson.dict()}}
    )
    
    return {"message": "Lesson added successfully", "lesson_id": lesson.id}

@app.post("/api/courses/{course_id}/enroll")
async def enroll_in_course(course_id: str, current_user: dict = Depends(get_current_user)):
    course = await db.courses.find_one({"id": course_id, "is_active": True})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Check if already enrolled
    if course_id in current_user.get("enrolled_courses", []):
        raise HTTPException(status_code=400, detail="Already enrolled in this course")
    
    # For free courses, enroll immediately
    if course["course_type"] == "free":
        # Update user's enrolled courses
        await db.users.update_one(
            {"id": current_user["id"]},
            {"$push": {"enrolled_courses": course_id}}
        )
        
        # Update course student count
        await db.courses.update_one(
            {"id": course_id},
            {"$inc": {"student_count": 1}}
        )
        
        # Create enrollment record
        enrollment = Enrollment(
            user_id=current_user["id"],
            course_id=course_id,
            payment_status="completed"
        )
        await db.enrollments.insert_one(enrollment.dict())
        
        return {"message": "Successfully enrolled in course", "enrollment_status": "completed"}
    
    # For paid courses, create pending enrollment
    enrollment = Enrollment(
        user_id=current_user["id"],
        course_id=course_id,
        payment_status="pending"
    )
    await db.enrollments.insert_one(enrollment.dict())
    
    return {
        "message": "Enrollment initiated. Please complete payment.",
        "enrollment_id": enrollment.id,
        "payment_required": True,
        "amount": course["price"]
    }

# Admin Routes
@app.get("/api/admin/dashboard")
async def admin_dashboard(current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    total_courses = await db.courses.count_documents({"is_active": True})
    total_students = await db.users.count_documents({"role": "student", "is_active": True})
    total_enrollments = await db.enrollments.count_documents({"payment_status": "completed"})
    
    return {
        "total_courses": total_courses,
        "total_students": total_students,
        "total_enrollments": total_enrollments
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)