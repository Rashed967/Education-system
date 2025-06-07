from fastapi import APIRouter, HTTPException, Depends
from ..database import database
from .auth import get_current_user

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/dashboard")
async def admin_dashboard(current_user: dict = Depends(get_current_user)):
    """Get admin dashboard statistics"""
    if current_user["role"] not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    total_courses = await database.courses.count_documents({"is_active": True})
    total_students = await database.users.count_documents({"role": "student", "is_active": True})
    total_enrollments = await database.enrollments.count_documents({"payment_status": "completed"})
    total_revenue = 0
    
    # Calculate total revenue from paid enrollments
    paid_enrollments = await database.enrollments.find(
        {"payment_status": "completed"}
    ).to_list(None)
    
    for enrollment in paid_enrollments:
        course = await database.courses.find_one({"id": enrollment["course_id"]})
        if course and course.get("price"):
            total_revenue += course["price"]
    
    return {
        "total_courses": total_courses,
        "total_students": total_students,
        "total_enrollments": total_enrollments,
        "total_revenue": total_revenue
    }

@router.get("/users")
async def get_all_users(current_user: dict = Depends(get_current_user)):
    """Get all users (admin only)"""
    if current_user["role"] not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    users = await database.users.find(
        {"is_active": True}, 
        {"password": 0}  # Exclude password field
    ).to_list(None)
    
    return {"users": users}

@router.put("/users/{user_id}/role")
async def update_user_role(
    user_id: str, 
    role_data: dict, 
    current_user: dict = Depends(get_current_user)
):
    """Update user role (super admin only)"""
    if current_user["role"] != "super_admin":
        raise HTTPException(status_code=403, detail="Super admin access required")
    
    new_role = role_data.get("role")
    if new_role not in ["student", "instructor", "admin", "super_admin"]:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    result = await database.users.update_one(
        {"id": user_id},
        {"$set": {"role": new_role}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "User role updated successfully"}

@router.get("/enrollments")
async def get_all_enrollments(current_user: dict = Depends(get_current_user)):
    """Get all enrollments (admin only)"""
    if current_user["role"] not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    enrollments = await database.enrollments.find({}).to_list(None)
    
    # Enrich with user and course information
    for enrollment in enrollments:
        user = await database.users.find_one({"id": enrollment["user_id"]})
        course = await database.courses.find_one({"id": enrollment["course_id"]})
        
        enrollment["user_name"] = user["full_name"] if user else "Unknown User"
        enrollment["user_email"] = user["email"] if user else "Unknown Email"
        enrollment["course_title"] = course["title"] if course else "Unknown Course"
    
    return {"enrollments": enrollments}