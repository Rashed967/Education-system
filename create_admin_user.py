import os
import asyncio
import motor.motor_asyncio
import hashlib
import uuid
from datetime import datetime

# Environment variables
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')

async def create_admin_user():
    # MongoDB setup
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
    db = client.islamic_institute
    
    # Check if admin user already exists
    admin_email = "admin@islamicinstitute.com"
    existing_admin = await db.users.find_one({"email": admin_email})
    
    if existing_admin:
        print(f"Admin user already exists: {admin_email}")
        return
    
    # Create admin user
    admin_user = {
        "id": str(uuid.uuid4()),
        "full_name": "Admin User",
        "email": admin_email,
        "password": hashlib.sha256("Admin123!".encode()).hexdigest(),
        "role": "admin",
        "phone": "+1234567890",
        "enrolled_courses": [],
        "created_at": datetime.utcnow(),
        "is_active": True
    }
    
    await db.users.insert_one(admin_user)
    print(f"Admin user created successfully: {admin_email}")
    print(f"Password: Admin123!")
    
    # Create a test course
    test_course = {
        "id": str(uuid.uuid4()),
        "title": "Introduction to Islamic Studies",
        "description": "A comprehensive introduction to the basics of Islamic studies, covering Quran, Hadith, and Islamic history.",
        "instructor_name": "Sheikh Abdullah",
        "course_type": "free",
        "thumbnail_url": "https://images.pexels.com/photos/9127599/pexels-photo-9127599.jpeg",
        "lessons": [
            {
                "id": str(uuid.uuid4()),
                "title": "Introduction to the Quran",
                "description": "Learn about the revelation, compilation, and structure of the Quran.",
                "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "video_type": "youtube",
                "duration": 45,
                "order": 1,
                "is_preview": True
            }
        ],
        "total_duration": 45,
        "student_count": 0,
        "created_at": datetime.utcnow(),
        "is_active": True
    }
    
    await db.courses.insert_one(test_course)
    print(f"Test course created successfully: {test_course['title']}")
    
    # Create a paid course
    paid_course = {
        "id": str(uuid.uuid4()),
        "title": "Advanced Quranic Arabic",
        "description": "Master the language of the Quran with this comprehensive course on Quranic Arabic.",
        "instructor_name": "Dr. Aisha Rahman",
        "course_type": "paid",
        "price": 99.99,
        "thumbnail_url": "https://images.pexels.com/photos/5490778/pexels-photo-5490778.jpeg",
        "lessons": [
            {
                "id": str(uuid.uuid4()),
                "title": "Arabic Alphabet and Pronunciation",
                "description": "Learn the Arabic alphabet and proper pronunciation.",
                "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "video_type": "youtube",
                "duration": 30,
                "order": 1,
                "is_preview": True
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Basic Grammar Rules",
                "description": "Understanding the fundamental grammar rules in Arabic.",
                "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "video_type": "youtube",
                "duration": 45,
                "order": 2,
                "is_preview": False
            }
        ],
        "total_duration": 75,
        "student_count": 0,
        "created_at": datetime.utcnow(),
        "is_active": True
    }
    
    await db.courses.insert_one(paid_course)
    print(f"Paid course created successfully: {paid_course['title']}")

if __name__ == "__main__":
    asyncio.run(create_admin_user())
