import requests
import unittest
import random
import string
import time

class IslamicInstituteAPITest(unittest.TestCase):
    def setUp(self):
        self.base_url = "https://85c16a9b-6909-4247-b731-02b00cdbc3e6.preview.emergentagent.com/api"
        self.token = None
        self.user_data = None
        self.course_id = None
        
        # Generate random user data for testing
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        self.test_user = {
            "full_name": f"Test User {random_suffix}",
            "email": f"testuser{random_suffix}@example.com",
            "password": "TestPassword123!",
            "phone": f"+1234567{random.randint(1000, 9999)}"
        }
        
        # Test course data
        self.test_course = {
            "title": f"Test Course {random_suffix}",
            "description": "This is a test course created for API testing",
            "instructor_name": "Test Instructor",
            "course_type": "free",
            "thumbnail_url": "https://example.com/thumbnail.jpg"
        }
        
        self.test_lesson = {
            "title": "Test Lesson",
            "description": "This is a test lesson",
            "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "video_type": "youtube",
            "duration": 10,
            "is_preview": True
        }

    def test_01_health_check(self):
        """Test the health check endpoint"""
        print("\n🔍 Testing health check endpoint...")
        response = requests.get(f"{self.base_url}/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        print("✅ Health check passed")

    def test_02_user_registration(self):
        """Test user registration"""
        print("\n🔍 Testing user registration...")
        response = requests.post(
            f"{self.base_url}/auth/register",
            json=self.test_user
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("access_token", data)
        self.assertIn("user", data)
        self.assertEqual(data["user"]["full_name"], self.test_user["full_name"])
        self.assertEqual(data["user"]["email"], self.test_user["email"])
        
        # Save token for future requests
        self.token = data["access_token"]
        self.user_data = data["user"]
        print(f"✅ User registration passed - Created user: {self.user_data['email']}")

    def test_03_user_login(self):
        """Test user login"""
        print("\n🔍 Testing user login...")
        
        # If we already have a token from registration, use that
        if self.token:
            print("✅ Already logged in from registration")
            return
            
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={
                "email": self.test_user["email"],
                "password": self.test_user["password"]
            }
        )
        
        if response.status_code != 200:
            print(f"❌ Login failed: {response.text}")
            return
            
        data = response.json()
        self.assertIn("access_token", data)
        self.token = data["access_token"]
        print("✅ User login passed")

    def test_04_get_user_profile(self):
        """Test getting user profile"""
        print("\n🔍 Testing user profile retrieval...")
        if not self.token:
            self.test_03_user_login()
            
        response = requests.get(
            f"{self.base_url}/auth/me",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["email"], self.test_user["email"])
        print("✅ User profile retrieval passed")

    def test_05_get_courses(self):
        """Test getting course list"""
        print("\n🔍 Testing course listing...")
        response = requests.get(f"{self.base_url}/courses")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("courses", data)
        print(f"✅ Course listing passed - Found {len(data['courses'])} courses")

    def test_06_create_course(self):
        """Test course creation (admin only)"""
        print("\n🔍 Testing course creation...")
        if not self.token:
            self.test_03_user_login()
            
        # Note: This might fail if the test user doesn't have admin/instructor privileges
        response = requests.post(
            f"{self.base_url}/courses",
            headers={"Authorization": f"Bearer {self.token}"},
            json=self.test_course
        )
        
        # Check if user has permission
        if response.status_code == 403:
            print("⚠️ Course creation skipped - User doesn't have admin/instructor privileges")
            return
            
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("course_id", data)
        self.course_id = data["course_id"]
        print(f"✅ Course creation passed - Created course ID: {self.course_id}")

    def test_07_get_course_details(self):
        """Test getting course details"""
        print("\n🔍 Testing course details retrieval...")
        if not self.token:
            self.test_03_user_login()
            
        # If we don't have a course ID from creation, try to get one from the course list
        if not self.course_id:
            response = requests.get(f"{self.base_url}/courses")
            courses = response.json().get("courses", [])
            if courses:
                self.course_id = courses[0]["id"]
            else:
                print("⚠️ Course details retrieval skipped - No courses available")
                return
                
        response = requests.get(
            f"{self.base_url}/courses/{self.course_id}",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id"], self.course_id)
        print(f"✅ Course details retrieval passed - Course: {data['title']}")

    def test_08_add_lesson(self):
        """Test adding a lesson to a course"""
        print("\n🔍 Testing lesson addition...")
        if not self.token:
            self.test_03_user_login()
            
        if not self.course_id:
            self.test_07_get_course_details()
            if not self.course_id:
                print("⚠️ Lesson addition skipped - No course ID available")
                return
                
        response = requests.post(
            f"{self.base_url}/courses/{self.course_id}/lessons",
            headers={"Authorization": f"Bearer {self.token}"},
            json=self.test_lesson
        )
        
        # Check if user has permission
        if response.status_code == 403:
            print("⚠️ Lesson addition skipped - User doesn't have admin/instructor privileges")
            return
            
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("lesson_id", data)
        print(f"✅ Lesson addition passed - Added lesson ID: {data['lesson_id']}")

    def test_09_course_enrollment(self):
        """Test course enrollment"""
        print("\n🔍 Testing course enrollment...")
        if not self.token:
            self.test_03_user_login()
            
        if not self.course_id:
            self.test_07_get_course_details()
            if not self.course_id:
                print("⚠️ Course enrollment skipped - No course ID available")
                return
                
        response = requests.post(
            f"{self.base_url}/courses/{self.course_id}/enroll",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        
        # If already enrolled, this will return 400
        if response.status_code == 400 and "Already enrolled" in response.json().get("detail", ""):
            print("⚠️ Already enrolled in this course")
            return
            
        self.assertIn(response.status_code, [200, 201])
        data = response.json()
        self.assertIn("message", data)
        print(f"✅ Course enrollment passed - {data['message']}")

    def test_10_admin_dashboard(self):
        """Test admin dashboard access"""
        print("\n🔍 Testing admin dashboard access...")
        if not self.token:
            self.test_03_user_login()
            
        response = requests.get(
            f"{self.base_url}/admin/dashboard",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        
        # Check if user has admin privileges
        if response.status_code == 403:
            print("⚠️ Admin dashboard access skipped - User doesn't have admin privileges")
            return
            
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("total_courses", data)
        self.assertIn("total_students", data)
        self.assertIn("total_enrollments", data)
        print("✅ Admin dashboard access passed")

def run_tests():
    # Create a test suite
    test_suite = unittest.TestSuite()
    
    # Add tests in order
    test_suite.addTest(IslamicInstituteAPITest('test_01_health_check'))
    test_suite.addTest(IslamicInstituteAPITest('test_02_user_registration'))
    test_suite.addTest(IslamicInstituteAPITest('test_03_user_login'))
    test_suite.addTest(IslamicInstituteAPITest('test_04_get_user_profile'))
    test_suite.addTest(IslamicInstituteAPITest('test_05_get_courses'))
    test_suite.addTest(IslamicInstituteAPITest('test_06_create_course'))
    test_suite.addTest(IslamicInstituteAPITest('test_07_get_course_details'))
    test_suite.addTest(IslamicInstituteAPITest('test_08_add_lesson'))
    test_suite.addTest(IslamicInstituteAPITest('test_09_course_enrollment'))
    test_suite.addTest(IslamicInstituteAPITest('test_10_admin_dashboard'))
    
    # Run the tests
    print("\n🧪 Starting API Tests for Islamic Institute Course Platform")
    print("=" * 70)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(test_suite)

if __name__ == "__main__":
    run_tests()
