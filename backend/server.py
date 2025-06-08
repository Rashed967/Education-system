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
    
    # Convert MongoDB ObjectId to string
    if '_id' in course:
        course['_id'] = str(course['_id'])
    
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
    
    # Create lesson with order field
    lesson_dict = lesson_data.dict()
    lesson_dict["order"] = len(course.get("lessons", [])) + 1
    lesson = Lesson(**lesson_dict)
    
    # Update course with new lesson
    await db.courses.update_one(
        {"id": course_id},
        {"$push": {"lessons": lesson.dict()}}
    )
    
    return {"message": "Lesson added successfully", "lesson_id": lesson.id}

@app.delete("/api/courses/{course_id}/lessons/{lesson_id}")
async def delete_lesson_from_course(course_id: str, lesson_id: str, current_user: dict = Depends(get_current_user)):
    # Check permissions
    if current_user["role"] not in ["admin", "super_admin", "instructor"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    course = await db.courses.find_one({"id": course_id})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Check if lesson exists
    lesson_exists = any(lesson["id"] == lesson_id for lesson in course.get("lessons", []))
    if not lesson_exists:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    # Remove lesson from course
    await db.courses.update_one(
        {"id": course_id},
        {"$pull": {"lessons": {"id": lesson_id}}}
    )
    
    return {"message": "Lesson deleted successfully"}

@app.put("/api/courses/{course_id}/lessons/{lesson_id}")
async def update_lesson_in_course(course_id: str, lesson_id: str, lesson_data: LessonCreate, current_user: dict = Depends(get_current_user)):
    # Check permissions
    if current_user["role"] not in ["admin", "super_admin", "instructor"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    course = await db.courses.find_one({"id": course_id})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Find the lesson and update it
    lessons = course.get("lessons", [])
    lesson_index = next((i for i, lesson in enumerate(lessons) if lesson["id"] == lesson_id), None)
    
    if lesson_index is None:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    # Update lesson data while preserving id and order
    updated_lesson = lesson_data.dict()
    updated_lesson["id"] = lesson_id
    updated_lesson["order"] = lessons[lesson_index]["order"]
    
    # Update the lesson in the array
    await db.courses.update_one(
        {"id": course_id, "lessons.id": lesson_id},
        {"$set": {"lessons.$": updated_lesson}}
    )
    
    return {"message": "Lesson updated successfully"}

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
    total_instructors = await db.users.count_documents({"role": "instructor", "is_active": True})
    
    # Get recent enrollments
    recent_enrollments = await db.enrollments.find(
        {"payment_status": "completed"}
    ).sort("enrolled_at", -1).limit(10).to_list(None)
    
    # Get course performance data
    course_stats = []
    courses = await db.courses.find({"is_active": True}).to_list(None)
    for course in courses:
        enrollments = await db.enrollments.count_documents({
            "course_id": course["id"], 
            "payment_status": "completed"
        })
        course_stats.append({
            "course_id": course["id"],
            "title": course["title"],
            "enrollments": enrollments,
            "revenue": course.get("price", 0) * enrollments if course["course_type"] == "paid" else 0
        })
    
    return {
        "total_courses": total_courses,
        "total_students": total_students,
        "total_instructors": total_instructors,
        "total_enrollments": total_enrollments,
        "recent_enrollments": recent_enrollments,
        "course_stats": course_stats
    }

@app.get("/api/admin/users")
async def get_all_users(current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    users = await db.users.find({}, {"password": 0}).to_list(None)
    # Convert MongoDB ObjectId to string and add enrollment info
    for user in users:
        if '_id' in user:
            user['_id'] = str(user['_id'])
        # Count enrollments for each user
        user["total_enrollments"] = await db.enrollments.count_documents({
            "user_id": user["id"], 
            "payment_status": "completed"
        })
    
    return {"users": users}

@app.put("/api/admin/users/{user_id}/role")
async def update_user_role(user_id: str, role_data: dict, current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    new_role = role_data.get("role")
    if new_role not in ["student", "instructor", "admin"]:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    # Prevent non-super-admin from creating other admins
    if new_role == "admin" and current_user["role"] != "super_admin":
        raise HTTPException(status_code=403, detail="Only super admin can create admin users")
    
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    await db.users.update_one(
        {"id": user_id},
        {"$set": {"role": new_role}}
    )
    
    return {"message": f"User role updated to {new_role}"}

@app.put("/api/admin/users/{user_id}/status")
async def update_user_status(user_id: str, status_data: dict, current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    is_active = status_data.get("is_active")
    if not isinstance(is_active, bool):
        raise HTTPException(status_code=400, detail="is_active must be a boolean")
    
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent admin from deactivating themselves
    if user_id == current_user["id"]:
        raise HTTPException(status_code=400, detail="Cannot change your own status")
    
    await db.users.update_one(
        {"id": user_id},
        {"$set": {"is_active": is_active}}
    )
    
    return {"message": f"User {'activated' if is_active else 'deactivated'} successfully"}

@app.get("/api/admin/courses")
async def get_all_courses_admin(current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    courses = await db.courses.find({}).to_list(None)
    # Add enrollment and revenue data
    for course in courses:
        if '_id' in course:
            course['_id'] = str(course['_id'])
        
        # Count enrollments
        enrollments = await db.enrollments.count_documents({
            "course_id": course["id"], 
            "payment_status": "completed"
        })
        course["total_enrollments"] = enrollments
        course["revenue"] = course.get("price", 0) * enrollments if course["course_type"] == "paid" else 0
        course["lesson_count"] = len(course.get("lessons", []))
    
    return {"courses": courses}

@app.delete("/api/admin/courses/{course_id}")
async def delete_course(course_id: str, current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    course = await db.courses.find_one({"id": course_id})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Check if course has enrollments
    enrollments = await db.enrollments.count_documents({"course_id": course_id})
    if enrollments > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot delete course with {enrollments} enrollments. Deactivate instead."
        )
    
    # Delete the course
    await db.courses.delete_one({"id": course_id})
    
    return {"message": "Course deleted successfully"}

@app.put("/api/admin/courses/{course_id}")
async def update_course_admin(course_id: str, course_data: CourseCreate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    course = await db.courses.find_one({"id": course_id})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Update course data
    update_data = course_data.dict()
    await db.courses.update_one(
        {"id": course_id},
        {"$set": update_data}
    )
    
    return {"message": "Course updated successfully"}

@app.get("/api/admin/enrollments")
async def get_all_enrollments(current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    enrollments = await db.enrollments.find({}).sort("enrolled_at", -1).to_list(None)
    
    # Enrich with user and course data
    for enrollment in enrollments:
        if '_id' in enrollment:
            enrollment['_id'] = str(enrollment['_id'])
        
        # Get user info
        user = await db.users.find_one({"id": enrollment["user_id"]}, {"password": 0})
        if user:
            enrollment["user_name"] = user["full_name"]
            enrollment["user_email"] = user["email"]
        
        # Get course info
        course = await db.courses.find_one({"id": enrollment["course_id"]})
        if course:
            enrollment["course_title"] = course["title"]
            enrollment["course_price"] = course.get("price", 0)
    
    return {"enrollments": enrollments}

@app.get("/api/admin/analytics")
async def get_analytics(current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Monthly enrollment trends (last 6 months)
    from datetime import datetime, timedelta
    import calendar
    
    monthly_data = []
    for i in range(6):
        # Calculate start and end of month
        target_date = datetime.now() - timedelta(days=30 * i)
        start_of_month = target_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if target_date.month == 12:
            end_of_month = start_of_month.replace(year=start_of_month.year + 1, month=1) - timedelta(seconds=1)
        else:
            end_of_month = start_of_month.replace(month=start_of_month.month + 1) - timedelta(seconds=1)
        
        # Count enrollments in this month
        enrollments = await db.enrollments.count_documents({
            "enrolled_at": {"$gte": start_of_month, "$lte": end_of_month},
            "payment_status": "completed"
        })
        
        monthly_data.append({
            "month": calendar.month_name[start_of_month.month],
            "year": start_of_month.year,
            "enrollments": enrollments
        })
    
    # Revenue by course type
    free_courses = await db.courses.count_documents({"course_type": "free", "is_active": True})
    paid_courses = await db.courses.count_documents({"course_type": "paid", "is_active": True})
    
    # Top performing courses
    courses = await db.courses.find({"is_active": True}).to_list(None)
    course_performance = []
    for course in courses:
        enrollments = await db.enrollments.count_documents({
            "course_id": course["id"], 
            "payment_status": "completed"
        })
        revenue = course.get("price", 0) * enrollments if course["course_type"] == "paid" else 0
        course_performance.append({
            "title": course["title"],
            "enrollments": enrollments,
            "revenue": revenue,
            "type": course["course_type"]
        })
    
    # Sort by enrollments
    course_performance.sort(key=lambda x: x["enrollments"], reverse=True)
    
    return {
        "monthly_trends": list(reversed(monthly_data)),  # Oldest to newest
        "course_type_distribution": {
            "free_courses": free_courses,
            "paid_courses": paid_courses
        },
        "top_courses": course_performance[:10]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)