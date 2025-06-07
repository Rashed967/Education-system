const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

class CourseService {
  async getCourses() {
    const response = await fetch(`${API_BASE_URL}/api/courses`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch courses');
    }
    
    const data = await response.json();
    return data.courses || [];
  }

  async getCourse(courseId, token) {
    const response = await fetch(`${API_BASE_URL}/api/courses/${courseId}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    
    if (!response.ok) {
      throw new Error('Failed to fetch course details');
    }
    
    return await response.json();
  }

  async createCourse(courseData, token) {
    const response = await fetch(`${API_BASE_URL}/api/courses`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(courseData)
    });
    
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.detail || 'Course creation failed');
    }
    
    return data;
  }

  async enrollInCourse(courseId, token) {
    const response = await fetch(`${API_BASE_URL}/api/courses/${courseId}/enroll`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` }
    });
    
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.detail || 'Enrollment failed');
    }
    
    return data;
  }

  async addLesson(courseId, lessonData, token) {
    const response = await fetch(`${API_BASE_URL}/api/courses/${courseId}/lessons`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(lessonData)
    });
    
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.detail || 'Failed to add lesson');
    }
    
    return data;
  }
}

export const courseService = new CourseService();