from fastapi import APIRouter, HTTPException, Depends
from typing import List
from ..models import Course, CourseCreate, Lesson, LessonCreate, Enrollment
from ..database import database
from ..utils.helpers import convert_objectid_to_string, format_course_response
from .auth import get_current_user

router = APIRouter(prefix="/courses", tags=["courses"])

@router.get("")
async def get_courses():
    """Get all active courses"""
    courses = await database.courses.find({"is_active": True}).to_list(None)
    return {"courses": convert_objectid_to_string(courses)}

@router.get("/{course_id}")
async def get_course(course_id: str, current_user: dict = Depends(get_current_user)):
    """Get course details"""
    course = await database.courses.find_one({"id": course_id, "is_active": True})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Check if user is enrolled
    is_enrolled = course_id in current_user.get("enrolled_courses", [])
    
    return format_course_response(course, is_enrolled)

@router.post("")
async def create_course(course_data: CourseCreate, current_user: dict = Depends(get_current_user)):
    """Create a new course (admin/instructor only)"""
    # Check if user is admin or instructor
    if current_user["role"] not in ["admin", "super_admin", "instructor"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    course = Course(**course_data.dict())
    course.instructor_id = current_user["id"]  # Set the instructor
    course_dict = course.dict()
    
    await database.courses.insert_one(course_dict)
    return {"message": "Course created successfully", "course_id": course.id}

@router.post("/{course_id}/lessons")
async def add_lesson_to_course(
    course_id: str, 
    lesson_data: LessonCreate, 
    current_user: dict = Depends(get_current_user)
):
    """Add a lesson to a course (admin/instructor only)"""
    # Check permissions
    if current_user["role"] not in ["admin", "super_admin", "instructor"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    course = await database.courses.find_one({"id": course_id})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Create lesson
    lesson = Lesson(**lesson_data.dict())
    lesson.order = len(course.get("lessons", [])) + 1
    
    # Update course with new lesson
    await database.courses.update_one(
        {"id": course_id},
        {"$push": {"lessons": lesson.dict()}}
    )
    
    return {"message": "Lesson added successfully", "lesson_id": lesson.id}

@router.post("/{course_id}/enroll")
async def enroll_in_course(course_id: str, current_user: dict = Depends(get_current_user)):
    """Enroll in a course"""
    course = await database.courses.find_one({"id": course_id, "is_active": True})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Check if already enrolled
    if course_id in current_user.get("enrolled_courses", []):
        raise HTTPException(status_code=400, detail="Already enrolled in this course")
    
    # For free courses, enroll immediately
    if course["course_type"] == "free":
        # Update user's enrolled courses
        await database.users.update_one(
            {"id": current_user["id"]},
            {"$push": {"enrolled_courses": course_id}}
        )
        
        # Update course student count
        await database.courses.update_one(
            {"id": course_id},
            {"$inc": {"student_count": 1}}
        )
        
        # Create enrollment record
        enrollment = Enrollment(
            user_id=current_user["id"],
            course_id=course_id,
            payment_status="completed"
        )
        await database.enrollments.insert_one(enrollment.dict())
        
        return {"message": "Successfully enrolled in course", "enrollment_status": "completed"}
    
    # For paid courses, create pending enrollment
    enrollment = Enrollment(
        user_id=current_user["id"],
        course_id=course_id,
        payment_status="pending"
    )
    await database.enrollments.insert_one(enrollment.dict())
    
    return {
        "message": "Enrollment initiated. Please complete payment.",
        "enrollment_id": enrollment.id,
        "payment_required": True,
        "amount": course["price"]
    }

@router.get("/{course_id}/lessons/{lesson_id}")
async def get_lesson(
    course_id: str, 
    lesson_id: str, 
    current_user: dict = Depends(get_current_user)
):
    """Get specific lesson details"""
    course = await database.courses.find_one({"id": course_id, "is_active": True})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Find the lesson
    lesson = None
    for l in course.get("lessons", []):
        if l["id"] == lesson_id:
            lesson = l
            break
    
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    # Check access permissions
    is_enrolled = course_id in current_user.get("enrolled_courses", [])
    
    if not is_enrolled and not lesson.get("is_preview", False):
        raise HTTPException(status_code=403, detail="Access denied. Please enroll in the course.")
    
    return lesson