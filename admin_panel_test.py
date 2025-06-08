import requests
import unittest
import random
import string
import time
import os
import json
from dotenv import load_dotenv
import pymongo
import hashlib

# Load environment variables from .env file
load_dotenv('/app/frontend/.env')

class AdvancedAdminAPITest(unittest.TestCase):
    def setUp(self):
        # Get backend URL from environment variable
        backend_url = os.getenv('REACT_APP_BACKEND_URL', 'https://7a9c659d-b44f-4b2a-afa4-cbfbea37ef14.preview.emergentagent.com')
        self.base_url = f"{backend_url}/api"
        self.admin_token = None
        self.regular_user_token = None
        self.admin_data = None
        self.regular_user_data = None
        self.test_user_id = None
        self.free_course_id = None
        self.paid_course_id = None
        self.course_with_enrollments_id = None
        
        # MongoDB connection
        mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
        self.mongo_client = pymongo.MongoClient(mongo_url)
        self.db = self.mongo_client.islamic_institute
        
        # Generate random user data for testing
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        
        # Admin user for testing admin operations
        self.admin_user = {
            "full_name": f"Admin User {random_suffix}",
            "email": f"adminuser{random_suffix}@example.com",
            "password": "AdminPassword123!",
            "phone": f"+1234567{random.randint(1000, 9999)}"
        }
        
        # Regular user for testing permission enforcement
        self.regular_user = {
            "full_name": f"Regular User {random_suffix}",
            "email": f"regularuser{random_suffix}@example.com",
            "password": "RegularPassword123!",
            "phone": f"+1234567{random.randint(1000, 9999)}"
        }
        
        # Test user for role/status updates
        self.test_user = {
            "full_name": f"Test User {random_suffix}",
            "email": f"testuser{random_suffix}@example.com",
            "password": "TestPassword123!",
            "phone": f"+1234567{random.randint(1000, 9999)}"
        }
        
        # Test free course data
        self.test_free_course = {
            "title": f"Free Test Course {random_suffix}",
            "description": "This is a free test course created for API testing",
            "instructor_name": "Test Instructor",
            "course_type": "free",
            "thumbnail_url": "https://example.com/thumbnail.jpg"
        }
        
        # Test paid course data
        self.test_paid_course = {
            "title": f"Paid Test Course {random_suffix}",
            "description": "This is a paid test course created for API testing",
            "instructor_name": "Test Instructor",
            "course_type": "paid",
            "price": 999.99,  # Price in BDT
            "thumbnail_url": "https://example.com/thumbnail.jpg"
        }
        
        # Updated course data for testing
        self.updated_course = {
            "title": f"Updated Course {random_suffix}",
            "description": "This course has been updated for testing",
            "instructor_name": "Updated Instructor",
            "course_type": "paid",
            "price": 1299.99,
            "thumbnail_url": "https://example.com/updated-thumbnail.jpg"
        }

    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def create_admin_user(self):
        """Create an admin user for testing admin operations"""
        print("\n🔍 Creating admin user for testing...")
        
        # Register the admin user
        response = requests.post(
            f"{self.base_url}/auth/register",
            json=self.admin_user
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to register admin user: {response.text}")
            return False
            
        data = response.json()
        self.admin_token = data["access_token"]
        self.admin_data = data["user"]
        
        # Update the user role to admin directly in the database
        try:
            result = self.db.users.update_one(
                {"email": self.admin_user["email"]},
                {"$set": {"role": "admin"}}
            )
            if result.modified_count > 0:
                print(f"✅ User role updated to admin for: {self.admin_data['email']}")
            else:
                print(f"⚠️ Failed to update user role to admin for: {self.admin_data['email']}")
                return False
        except Exception as e:
            print(f"❌ Error updating user role: {str(e)}")
            return False
        
        # Login again to get a token with admin privileges
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={
                "email": self.admin_user["email"],
                "password": self.admin_user["password"]
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            self.admin_token = data["access_token"]
            print(f"✅ Admin user created and logged in: {self.admin_data['email']}")
            return True
        else:
            print(f"❌ Admin login failed: {response.text}")
            return False

    def create_regular_user(self):
        """Create a regular user for testing permission enforcement"""
        print("\n🔍 Creating regular user for testing...")
        
        # Register the regular user
        response = requests.post(
            f"{self.base_url}/auth/register",
            json=self.regular_user
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to register regular user: {response.text}")
            return False
            
        data = response.json()
        self.regular_user_token = data["access_token"]
        self.regular_user_data = data["user"]
        print(f"✅ Regular user created: {self.regular_user_data['email']}")
        return True

    def create_test_user(self):
        """Create a test user for role/status updates"""
        print("\n🔍 Creating test user for role/status updates...")
        
        # Register the test user
        response = requests.post(
            f"{self.base_url}/auth/register",
            json=self.test_user
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to register test user: {response.text}")
            return False
            
        data = response.json()
        self.test_user_id = data["user"]["id"]
        print(f"✅ Test user created: {self.test_user['email']} with ID: {self.test_user_id}")
        return True

    def create_test_courses(self):
        """Create test courses for testing course management APIs"""
        print("\n🔍 Creating test courses...")
        
        if not self.admin_token:
            if not self.create_admin_user():
                return False
        
        # Create free course
        response = requests.post(
            f"{self.base_url}/courses",
            headers={"Authorization": f"Bearer {self.admin_token}"},
            json=self.test_free_course
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to create free course: {response.text}")
            return False
            
        data = response.json()
        self.free_course_id = data["course_id"]
        print(f"✅ Free course created with ID: {self.free_course_id}")
        
        # Create paid course
        response = requests.post(
            f"{self.base_url}/courses",
            headers={"Authorization": f"Bearer {self.admin_token}"},
            json=self.test_paid_course
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to create paid course: {response.text}")
            return False
            
        data = response.json()
        self.paid_course_id = data["course_id"]
        print(f"✅ Paid course created with ID: {self.paid_course_id}")
        
        return True

    def create_course_with_enrollments(self):
        """Create a course and enroll a user in it for testing deletion restrictions"""
        print("\n🔍 Creating course with enrollments...")
        
        if not self.admin_token:
            if not self.create_admin_user():
                return False
                
        if not self.regular_user_token:
            if not self.create_regular_user():
                return False
        
        # Create a free course
        course_data = {
            "title": f"Course With Enrollments {random.randint(1000, 9999)}",
            "description": "This course is used to test deletion restrictions",
            "instructor_name": "Test Instructor",
            "course_type": "free",
            "thumbnail_url": "https://example.com/thumbnail.jpg"
        }
        
        response = requests.post(
            f"{self.base_url}/courses",
            headers={"Authorization": f"Bearer {self.admin_token}"},
            json=course_data
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to create course with enrollments: {response.text}")
            return False
            
        data = response.json()
        self.course_with_enrollments_id = data["course_id"]
        
        # Enroll the regular user in this course
        response = requests.post(
            f"{self.base_url}/courses/{self.course_with_enrollments_id}/enroll",
            headers={"Authorization": f"Bearer {self.regular_user_token}"}
        )
        
        if response.status_code not in [200, 201]:
            print(f"❌ Failed to enroll user in course: {response.text}")
            return False
            
        print(f"✅ Created course with enrollments, ID: {self.course_with_enrollments_id}")
        return True

    def test_01_setup(self):
        """Set up test data"""
        print("\n🔍 Setting up test data...")
        
        # Create admin user
        if not self.create_admin_user():
            self.fail("Failed to create admin user")
            
        # Create regular user
        if not self.create_regular_user():
            self.fail("Failed to create regular user")
            
        # Create test user for role/status updates
        if not self.create_test_user():
            self.fail("Failed to create test user")
            
        # Create test courses
        if not self.create_test_courses():
            self.fail("Failed to create test courses")
            
        # Create course with enrollments
        if not self.create_course_with_enrollments():
            self.fail("Failed to create course with enrollments")
            
        print("✅ Test setup completed successfully")

    def test_02_enhanced_admin_dashboard(self):
        """Test the enhanced admin dashboard API"""
        print("\n🔍 Testing enhanced admin dashboard API...")
        
        # Test with admin user
        response = requests.get(
            f"{self.base_url}/admin/dashboard",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify all required fields are present
        required_fields = [
            "total_courses", "total_students", "total_instructors", 
            "total_enrollments", "recent_enrollments", "course_stats"
        ]
        
        for field in required_fields:
            self.assertIn(field, data)
            
        # Verify course stats contain required fields
        if data["course_stats"]:
            course_stat = data["course_stats"][0]
            self.assertIn("course_id", course_stat)
            self.assertIn("title", course_stat)
            self.assertIn("enrollments", course_stat)
            self.assertIn("revenue", course_stat)
            
        print("✅ Enhanced admin dashboard API test passed")
        
        # Test with regular user (should be denied)
        response = requests.get(
            f"{self.base_url}/admin/dashboard",
            headers={"Authorization": f"Bearer {self.regular_user_token}"}
        )
        
        self.assertEqual(response.status_code, 403)
        print("✅ Permission enforcement test passed - Regular user denied access")

    def test_03_user_management_get_all_users(self):
        """Test getting all users with enrollment data"""
        print("\n🔍 Testing GET /api/admin/users API...")
        
        # Test with admin user
        response = requests.get(
            f"{self.base_url}/admin/users",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn("users", data)
        self.assertTrue(len(data["users"]) > 0)
        
        # Verify user data contains enrollment info
        user = data["users"][0]
        self.assertIn("total_enrollments", user)
        
        print("✅ GET all users API test passed")
        
        # Test with regular user (should be denied)
        response = requests.get(
            f"{self.base_url}/admin/users",
            headers={"Authorization": f"Bearer {self.regular_user_token}"}
        )
        
        self.assertEqual(response.status_code, 403)
        print("✅ Permission enforcement test passed - Regular user denied access")

    def test_04_user_management_update_role(self):
        """Test updating user role"""
        print("\n🔍 Testing PUT /api/admin/users/{user_id}/role API...")
        
        if not self.test_user_id:
            self.fail("Test user ID not available")
            
        # Test with admin user - Update to instructor
        response = requests.put(
            f"{self.base_url}/admin/users/{self.test_user_id}/role",
            headers={"Authorization": f"Bearer {self.admin_token}"},
            json={"role": "instructor"}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)
        self.assertIn("instructor", data["message"])
        
        # Verify role was updated
        response = requests.get(
            f"{self.base_url}/admin/users",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        users = response.json()["users"]
        test_user = next((user for user in users if user["id"] == self.test_user_id), None)
        self.assertIsNotNone(test_user)
        self.assertEqual(test_user["role"], "instructor")
        
        print("✅ Update user role to instructor test passed")
        
        # Update back to student
        response = requests.put(
            f"{self.base_url}/admin/users/{self.test_user_id}/role",
            headers={"Authorization": f"Bearer {self.admin_token}"},
            json={"role": "student"}
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Verify role was updated back
        response = requests.get(
            f"{self.base_url}/admin/users",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        users = response.json()["users"]
        test_user = next((user for user in users if user["id"] == self.test_user_id), None)
        self.assertIsNotNone(test_user)
        self.assertEqual(test_user["role"], "student")
        
        print("✅ Update user role back to student test passed")
        
        # Test with regular user (should be denied)
        response = requests.put(
            f"{self.base_url}/admin/users/{self.test_user_id}/role",
            headers={"Authorization": f"Bearer {self.regular_user_token}"},
            json={"role": "instructor"}
        )
        
        self.assertEqual(response.status_code, 403)
        print("✅ Permission enforcement test passed - Regular user denied access")
        
        # Test with invalid role
        response = requests.put(
            f"{self.base_url}/admin/users/{self.test_user_id}/role",
            headers={"Authorization": f"Bearer {self.admin_token}"},
            json={"role": "invalid_role"}
        )
        
        self.assertEqual(response.status_code, 400)
        print("✅ Invalid role validation test passed")

    def test_05_user_management_update_status(self):
        """Test activating/deactivating users"""
        print("\n🔍 Testing PUT /api/admin/users/{user_id}/status API...")
        
        if not self.test_user_id:
            self.fail("Test user ID not available")
            
        # Test with admin user - Deactivate user
        response = requests.put(
            f"{self.base_url}/admin/users/{self.test_user_id}/status",
            headers={"Authorization": f"Bearer {self.admin_token}"},
            json={"is_active": False}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)
        self.assertIn("deactivated", data["message"])
        
        # Verify status was updated
        response = requests.get(
            f"{self.base_url}/admin/users",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        users = response.json()["users"]
        test_user = next((user for user in users if user["id"] == self.test_user_id), None)
        self.assertIsNotNone(test_user)
        self.assertEqual(test_user["is_active"], False)
        
        print("✅ Deactivate user test passed")
        
        # Reactivate user
        response = requests.put(
            f"{self.base_url}/admin/users/{self.test_user_id}/status",
            headers={"Authorization": f"Bearer {self.admin_token}"},
            json={"is_active": True}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("activated", data["message"])
        
        # Verify status was updated back
        response = requests.get(
            f"{self.base_url}/admin/users",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        users = response.json()["users"]
        test_user = next((user for user in users if user["id"] == self.test_user_id), None)
        self.assertIsNotNone(test_user)
        self.assertEqual(test_user["is_active"], True)
        
        print("✅ Reactivate user test passed")
        
        # Test with regular user (should be denied)
        response = requests.put(
            f"{self.base_url}/admin/users/{self.test_user_id}/status",
            headers={"Authorization": f"Bearer {self.regular_user_token}"},
            json={"is_active": False}
        )
        
        self.assertEqual(response.status_code, 403)
        print("✅ Permission enforcement test passed - Regular user denied access")
        
        # Test with invalid data
        response = requests.put(
            f"{self.base_url}/admin/users/{self.test_user_id}/status",
            headers={"Authorization": f"Bearer {self.admin_token}"},
            json={"is_active": "not_a_boolean"}
        )
        
        self.assertEqual(response.status_code, 400)
        print("✅ Invalid status validation test passed")

    def test_06_course_management_get_all_courses(self):
        """Test getting all courses with enrollment and revenue data"""
        print("\n🔍 Testing GET /api/admin/courses API...")
        
        # Test with admin user
        response = requests.get(
            f"{self.base_url}/admin/courses",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn("courses", data)
        self.assertTrue(len(data["courses"]) > 0)
        
        # Verify course data contains enrollment and revenue info
        course = data["courses"][0]
        self.assertIn("total_enrollments", course)
        self.assertIn("revenue", course)
        self.assertIn("lesson_count", course)
        
        print("✅ GET all courses API test passed")
        
        # Test with regular user (should be denied)
        response = requests.get(
            f"{self.base_url}/admin/courses",
            headers={"Authorization": f"Bearer {self.regular_user_token}"}
        )
        
        self.assertEqual(response.status_code, 403)
        print("✅ Permission enforcement test passed - Regular user denied access")

    def test_07_course_management_update_course(self):
        """Test updating course details"""
        print("\n🔍 Testing PUT /api/admin/courses/{course_id} API...")
        
        if not self.paid_course_id:
            self.fail("Paid course ID not available")
            
        # Test with admin user
        response = requests.put(
            f"{self.base_url}/admin/courses/{self.paid_course_id}",
            headers={"Authorization": f"Bearer {self.admin_token}"},
            json=self.updated_course
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)
        self.assertIn("updated", data["message"])
        
        # Verify course was updated
        response = requests.get(
            f"{self.base_url}/courses/{self.paid_course_id}",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        self.assertEqual(response.status_code, 200)
        course = response.json()
        self.assertEqual(course["title"], self.updated_course["title"])
        self.assertEqual(course["description"], self.updated_course["description"])
        self.assertEqual(course["instructor_name"], self.updated_course["instructor_name"])
        self.assertEqual(course["price"], self.updated_course["price"])
        
        print("✅ Update course test passed")
        
        # Test with regular user (should be denied)
        response = requests.put(
            f"{self.base_url}/admin/courses/{self.paid_course_id}",
            headers={"Authorization": f"Bearer {self.regular_user_token}"},
            json=self.updated_course
        )
        
        self.assertEqual(response.status_code, 403)
        print("✅ Permission enforcement test passed - Regular user denied access")

    def test_08_course_management_delete_course(self):
        """Test deleting a course"""
        print("\n🔍 Testing DELETE /api/admin/courses/{course_id} API...")
        
        if not self.free_course_id:
            self.fail("Free course ID not available")
            
        # Test with admin user
        response = requests.delete(
            f"{self.base_url}/admin/courses/{self.free_course_id}",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)
        self.assertIn("deleted", data["message"])
        
        # Verify course was deleted
        response = requests.get(
            f"{self.base_url}/courses/{self.free_course_id}",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        self.assertEqual(response.status_code, 404)
        print("✅ Delete course test passed")
        
        # Test deleting a course with enrollments (should fail)
        if not self.course_with_enrollments_id:
            self.fail("Course with enrollments ID not available")
            
        response = requests.delete(
            f"{self.base_url}/admin/courses/{self.course_with_enrollments_id}",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("detail", data)
        self.assertIn("Cannot delete course with", data["detail"])
        
        print("✅ Delete course with enrollments test passed - Correctly prevented deletion")
        
        # Test with regular user (should be denied)
        response = requests.delete(
            f"{self.base_url}/admin/courses/{self.paid_course_id}",
            headers={"Authorization": f"Bearer {self.regular_user_token}"}
        )
        
        self.assertEqual(response.status_code, 403)
        print("✅ Permission enforcement test passed - Regular user denied access")

    def test_09_analytics_api(self):
        """Test the analytics API"""
        print("\n🔍 Testing GET /api/admin/analytics API...")
        
        # Test with admin user
        response = requests.get(
            f"{self.base_url}/admin/analytics",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify all required fields are present
        required_fields = [
            "monthly_trends", "course_type_distribution", "top_courses"
        ]
        
        for field in required_fields:
            self.assertIn(field, data)
            
        # Verify monthly trends data
        self.assertTrue(len(data["monthly_trends"]) > 0)
        if data["monthly_trends"]:
            month_data = data["monthly_trends"][0]
            self.assertIn("month", month_data)
            self.assertIn("year", month_data)
            self.assertIn("enrollments", month_data)
            
        # Verify course type distribution
        self.assertIn("free_courses", data["course_type_distribution"])
        self.assertIn("paid_courses", data["course_type_distribution"])
        
        # Verify top courses
        if data["top_courses"]:
            top_course = data["top_courses"][0]
            self.assertIn("title", top_course)
            self.assertIn("enrollments", top_course)
            self.assertIn("revenue", top_course)
            self.assertIn("type", top_course)
            
        print("✅ Analytics API test passed")
        
        # Test with regular user (should be denied)
        response = requests.get(
            f"{self.base_url}/admin/analytics",
            headers={"Authorization": f"Bearer {self.regular_user_token}"}
        )
        
        self.assertEqual(response.status_code, 403)
        print("✅ Permission enforcement test passed - Regular user denied access")

    def test_10_enrollments_api(self):
        """Test the enrollments API"""
        print("\n🔍 Testing GET /api/admin/enrollments API...")
        
        # Test with admin user
        response = requests.get(
            f"{self.base_url}/admin/enrollments",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn("enrollments", data)
        
        # Verify enrollment data contains user and course info
        if data["enrollments"]:
            enrollment = data["enrollments"][0]
            self.assertIn("user_name", enrollment)
            self.assertIn("user_email", enrollment)
            self.assertIn("course_title", enrollment)
            self.assertIn("course_price", enrollment)
            self.assertIn("payment_status", enrollment)
            self.assertIn("enrolled_at", enrollment)
            
        print("✅ Enrollments API test passed")
        
        # Test with regular user (should be denied)
        response = requests.get(
            f"{self.base_url}/admin/enrollments",
            headers={"Authorization": f"Bearer {self.regular_user_token}"}
        )
        
        self.assertEqual(response.status_code, 403)
        print("✅ Permission enforcement test passed - Regular user denied access")

def run_tests():
    print("\n🧪 Starting Advanced Admin Panel API Tests")
    print("=" * 70)
    
    # Create a test instance
    test_instance = AdvancedAdminAPITest()
    test_instance.setUp()
    
    # Run tests in sequence
    try:
        # Setup test data
        test_instance.test_01_setup()
        
        # Test enhanced admin dashboard
        test_instance.test_02_enhanced_admin_dashboard()
        
        # Test user management APIs
        test_instance.test_03_user_management_get_all_users()
        test_instance.test_04_user_management_update_role()
        test_instance.test_05_user_management_update_status()
        
        # Test course management APIs
        test_instance.test_06_course_management_get_all_courses()
        test_instance.test_07_course_management_update_course()
        test_instance.test_08_course_management_delete_course()
        
        # Test analytics API
        test_instance.test_09_analytics_api()
        
        # Test enrollments API
        test_instance.test_10_enrollments_api()
        
        print("\n✅ All advanced admin panel API tests completed successfully")
    except Exception as e:
        print(f"\n❌ Tests failed: {str(e)}")
    
    print("\n📊 Test Summary:")
    print("=" * 70)
    print("1. Enhanced Admin Dashboard:")
    print("   - Tested GET /api/admin/dashboard endpoint")
    print("   - Verified comprehensive stats including total users, instructors, enrollments")
    print("   - Verified course performance data")
    print("2. User Management APIs:")
    print("   - Tested GET /api/admin/users - Get all users with enrollment data")
    print("   - Tested PUT /api/admin/users/{user_id}/role - Update user role")
    print("   - Tested PUT /api/admin/users/{user_id}/status - Activate/deactivate users")
    print("3. Course Management APIs:")
    print("   - Tested GET /api/admin/courses - Get all courses with enrollment and revenue data")
    print("   - Tested PUT /api/admin/courses/{course_id} - Update course details")
    print("   - Tested DELETE /api/admin/courses/{course_id} - Delete course")
    print("   - Verified course deletion fails if enrollments exist")
    print("4. Analytics API:")
    print("   - Tested GET /api/admin/analytics")
    print("   - Verified monthly enrollment trends, course distribution, top performing courses")
    print("5. Enrollments API:")
    print("   - Tested GET /api/admin/enrollments")
    print("   - Verified all enrollments with user and course details")
    print("6. Permission Enforcement:")
    print("   - Verified all admin endpoints deny access to non-admin users")

if __name__ == "__main__":
    run_tests()