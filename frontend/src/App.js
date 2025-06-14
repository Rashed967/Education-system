import React, { useState, useEffect } from 'react';
import './App.css';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

function App() {
  const [user, setUser] = useState(null);
  const [courses, setCourses] = useState([]);
  const [currentView, setCurrentView] = useState('home');
  const [selectedCourse, setSelectedCourse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Auth forms state
  const [loginForm, setLoginForm] = useState({ email: '', password: '' });
  const [registerForm, setRegisterForm] = useState({ 
    full_name: '', 
    email: '', 
    password: '', 
    phone: '' 
  });

  // Course creation form
  const [courseForm, setCourseForm] = useState({
    title: '',
    description: '',
    instructor_name: '',
    course_type: 'free',
    price: '',
    thumbnail_url: ''
  });

  // Lesson creation form
  const [lessonForm, setLessonForm] = useState({
    title: '',
    description: '',
    video_url: '',
    video_type: 'youtube',
    duration: '',
    is_preview: false
  });

  // Add lesson management state
  const [showAddLesson, setShowAddLesson] = useState(false);
  const [editingLessonId, setEditingLessonId] = useState(null);
  const [showLessonManagement, setShowLessonManagement] = useState(false);

  // Admin panel state
  const [adminData, setAdminData] = useState({
    users: [],
    courses: [],
    enrollments: [],
    analytics: null,
    dashboard: null
  });
  const [adminLoading, setAdminLoading] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      fetchUserInfo(token);
    }
    fetchCourses();
  }, []);

  const fetchUserInfo = async (token) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
      } else {
        localStorage.removeItem('token');
      }
    } catch (error) {
      console.error('Error fetching user info:', error);
      localStorage.removeItem('token');
    }
  };

  const fetchCourses = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/courses`);
      const data = await response.json();
      setCourses(data.courses || []);
    } catch (error) {
      console.error('Error fetching courses:', error);
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(loginForm)
      });
      
      const data = await response.json();
      
      if (response.ok) {
        localStorage.setItem('token', data.access_token);
        setUser(data.user);
        setCurrentView('dashboard');
        setSuccess('Login successful!');
        setLoginForm({ email: '', password: '' });
      } else {
        setError(data.detail || 'Login failed');
      }
    } catch (error) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(registerForm)
      });
      
      const data = await response.json();
      
      if (response.ok) {
        localStorage.setItem('token', data.access_token);
        setUser(data.user);
        setCurrentView('dashboard');
        setSuccess('Registration successful!');
        setRegisterForm({ full_name: '', email: '', password: '', phone: '' });
      } else {
        setError(data.detail || 'Registration failed');
      }
    } catch (error) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setUser(null);
    setCurrentView('home');
    setSuccess('Logged out successfully');
  };

  const handleCourseView = async (courseId) => {
    if (!user) {
      setError('Please login to view course details');
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/api/courses/${courseId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const course = await response.json();
        setSelectedCourse(course);
        setCurrentView('course-detail');
      } else {
        setError('Failed to load course details');
      }
    } catch (error) {
      setError('Network error. Please try again.');
    }
  };

  const handleEnrollment = async (courseId) => {
    if (!user) {
      setError('Please login to enroll');
      return;
    }

    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/api/courses/${courseId}/enroll`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setSuccess(data.message);
        fetchUserInfo(token); // Refresh user data
        if (selectedCourse) {
          handleCourseView(courseId); // Refresh course data
        }
      } else {
        setError(data.detail || 'Enrollment failed');
      }
    } catch (error) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateCourse = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const token = localStorage.getItem('token');
      const formData = { ...courseForm };
      if (formData.price) {
        formData.price = parseFloat(formData.price);
      }

      const response = await fetch(`${API_BASE_URL}/api/courses`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(formData)
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setSuccess('Course created successfully!');
        setCourseForm({
          title: '',
          description: '',
          instructor_name: '',
          course_type: 'free',
          price: '',
          thumbnail_url: ''
        });
        fetchCourses();
      } else {
        setError(data.detail || 'Course creation failed');
      }
    } catch (error) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleAddLesson = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const token = localStorage.getItem('token');
      const formData = { ...lessonForm };
      if (formData.duration) {
        formData.duration = parseInt(formData.duration);
      }

      let response;
      if (editingLessonId) {
        // Update existing lesson
        response = await fetch(`${API_BASE_URL}/api/courses/${selectedCourse.id}/lessons/${editingLessonId}`, {
          method: 'PUT',
          headers: { 
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify(formData)
        });
      } else {
        // Add new lesson
        response = await fetch(`${API_BASE_URL}/api/courses/${selectedCourse.id}/lessons`, {
          method: 'POST',
          headers: { 
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify(formData)
        });
      }
      
      const data = await response.json();
      
      if (response.ok) {
        setSuccess(editingLessonId ? 'Lesson updated successfully!' : 'Lesson added successfully!');
        setLessonForm({
          title: '',
          description: '',
          video_url: '',
          video_type: 'youtube',
          duration: '',
          is_preview: false
        });
        setShowAddLesson(false);
        setEditingLessonId(null);
        // Refresh course data to show updated/new lesson
        handleCourseView(selectedCourse.id);
      } else {
        setError(data.detail || 'Lesson operation failed');
      }
    } catch (error) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteLesson = async (lessonId) => {
    if (!window.confirm('Are you sure you want to delete this lesson?')) {
      return;
    }

    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/api/courses/${selectedCourse.id}/lessons/${lessonId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        setSuccess('Lesson deleted successfully!');
        // Refresh course data
        handleCourseView(selectedCourse.id);
      } else {
        const data = await response.json();
        setError(data.detail || 'Lesson deletion failed');
      }
    } catch (error) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Admin functions
  const fetchAdminDashboard = async () => {
    setAdminLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/api/admin/dashboard`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setAdminData(prev => ({ ...prev, dashboard: data }));
      }
    } catch (error) {
      console.error('Error fetching admin dashboard:', error);
    } finally {
      setAdminLoading(false);
    }
  };

  const fetchAdminUsers = async () => {
    setAdminLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/api/admin/users`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setAdminData(prev => ({ ...prev, users: data.users }));
      }
    } catch (error) {
      console.error('Error fetching users:', error);
    } finally {
      setAdminLoading(false);
    }
  };

  const fetchAdminCourses = async () => {
    setAdminLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/api/admin/courses`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setAdminData(prev => ({ ...prev, courses: data.courses }));
      }
    } catch (error) {
      console.error('Error fetching admin courses:', error);
    } finally {
      setAdminLoading(false);
    }
  };

  const fetchAdminAnalytics = async () => {
    setAdminLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/api/admin/analytics`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setAdminData(prev => ({ ...prev, analytics: data }));
      }
    } catch (error) {
      console.error('Error fetching analytics:', error);
    } finally {
      setAdminLoading(false);
    }
  };

  const handleUpdateUserRole = async (userId, newRole) => {
    if (!window.confirm(`Are you sure you want to change this user's role to ${newRole}?`)) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/api/admin/users/${userId}/role`, {
        method: 'PUT',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ role: newRole })
      });
      
      if (response.ok) {
        setSuccess('User role updated successfully!');
        fetchAdminUsers(); // Refresh users list
      } else {
        const data = await response.json();
        setError(data.detail || 'Failed to update user role');
      }
    } catch (error) {
      setError('Network error. Please try again.');
    }
  };

  const handleUpdateUserStatus = async (userId, isActive) => {
    const action = isActive ? 'activate' : 'deactivate';
    if (!window.confirm(`Are you sure you want to ${action} this user?`)) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/api/admin/users/${userId}/status`, {
        method: 'PUT',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ is_active: isActive })
      });
      
      if (response.ok) {
        setSuccess(`User ${action}d successfully!`);
        fetchAdminUsers(); // Refresh users list
      } else {
        const data = await response.json();
        setError(data.detail || `Failed to ${action} user`);
      }
    } catch (error) {
      setError('Network error. Please try again.');
    }
  };

  const handleDeleteCourse = async (courseId) => {
    if (!window.confirm('Are you sure you want to delete this course? This action cannot be undone.')) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/api/admin/courses/${courseId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        setSuccess('Course deleted successfully!');
        fetchAdminCourses(); // Refresh courses list
      } else {
        const data = await response.json();
        setError(data.detail || 'Failed to delete course');
      }
    } catch (error) {
      setError('Network error. Please try again.');
    }
  };

  const getVideoEmbedUrl = (url, type) => {
    if (type === 'youtube') {
      const videoId = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)/);
      return videoId ? `https://www.youtube.com/embed/${videoId[1]}` : url;
    } else if (type === 'vimeo') {
      const videoId = url.match(/vimeo\.com\/(\d+)/);
      return videoId ? `https://player.vimeo.com/video/${videoId[1]}` : url;
    }
    return url;
  };

  const clearMessages = () => {
    setError('');
    setSuccess('');
  };

  // Home/Landing Page
  if (currentView === 'home') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-emerald-50 to-teal-100">
        {/* Navigation */}
        <nav className="bg-white shadow-lg">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <h1 className="text-2xl font-bold text-emerald-600">Islamic Institute</h1>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                {user ? (
                  <>
                    <span className="text-gray-700">Welcome, {user.full_name}</span>
                    <button
                      onClick={() => setCurrentView('dashboard')}
                      className="bg-emerald-600 text-white px-4 py-2 rounded-md hover:bg-emerald-700"
                    >
                      Dashboard
                    </button>
                    <button
                      onClick={handleLogout}
                      className="bg-gray-600 text-white px-4 py-2 rounded-md hover:bg-gray-700"
                    >
                      Logout
                    </button>
                  </>
                ) : (
                  <>
                    <button
                      onClick={() => setCurrentView('login')}
                      className="text-emerald-600 hover:text-emerald-800"
                    >
                      Login
                    </button>
                    <button
                      onClick={() => setCurrentView('register')}
                      className="bg-emerald-600 text-white px-4 py-2 rounded-md hover:bg-emerald-700"
                    >
                      Register
                    </button>
                  </>
                )}
              </div>
            </div>
          </div>
        </nav>

        {/* Hero Section */}
        <div className="relative">
          <div className="absolute inset-0">
            <img
              className="w-full h-96 object-cover"
              src="https://images.pexels.com/photos/9127599/pexels-photo-9127599.jpeg"
              alt="Islamic Education"
            />
            <div className="absolute inset-0 bg-emerald-600 opacity-75"></div>
          </div>
          <div className="relative max-w-7xl mx-auto py-24 px-4 sm:py-32 sm:px-6 lg:px-8">
            <h1 className="text-4xl font-extrabold tracking-tight text-white sm:text-5xl lg:text-6xl">
              Learn with Purpose
            </h1>
            <p className="mt-6 text-xl text-emerald-100 max-w-3xl">
              Discover authentic Islamic education through our comprehensive online courses. 
              Learn from qualified instructors and grow in your faith and knowledge.
            </p>
            <div className="mt-10">
              {!user && (
                <button
                  onClick={() => setCurrentView('register')}
                  className="bg-white text-emerald-600 px-8 py-3 rounded-md text-lg font-medium hover:bg-emerald-50"
                >
                  Start Learning Today
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Courses Preview */}
        <div className="max-w-7xl mx-auto py-16 px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-extrabold text-gray-900 text-center mb-12">
            Featured Courses
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {courses.slice(0, 6).map(course => (
              <div key={course.id} className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
                {course.thumbnail_url && (
                  <img
                    className="w-full h-48 object-cover"
                    src={course.thumbnail_url}
                    alt={course.title}
                  />
                )}
                <div className="p-6">
                  <div className="flex items-center justify-between mb-2">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      course.course_type === 'free' 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-blue-100 text-blue-800'
                    }`}>
                      {course.course_type === 'free' ? 'Free' : `৳${course.price}`}
                    </span>
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">{course.title}</h3>
                  <p className="text-gray-600 text-sm mb-4">{course.description.substring(0, 100)}...</p>
                  <p className="text-sm text-gray-500 mb-4">Instructor: {course.instructor_name}</p>
                  <button
                    onClick={() => user ? handleCourseView(course.id) : setCurrentView('login')}
                    className="w-full bg-emerald-600 text-white py-2 rounded-md hover:bg-emerald-700"
                  >
                    View Course
                  </button>
                </div>
              </div>
            ))}
          </div>
          {courses.length > 6 && (
            <div className="text-center mt-12">
              <button
                onClick={() => user ? setCurrentView('courses') : setCurrentView('login')}
                className="bg-emerald-600 text-white px-8 py-3 rounded-md hover:bg-emerald-700"
              >
                View All Courses
              </button>
            </div>
          )}
        </div>
      </div>
    );
  }

  // Login Page
  if (currentView === 'login') {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
        <div className="sm:mx-auto sm:w-full sm:max-w-md">
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Sign in to your account
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Or{' '}
            <button
              onClick={() => setCurrentView('register')}
              className="font-medium text-emerald-600 hover:text-emerald-500"
            >
              create a new account
            </button>
          </p>
        </div>

        <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
          <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
            {error && (
              <div className="mb-4 bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded">
                {error}
                <button onClick={clearMessages} className="float-right text-red-400 hover:text-red-600">×</button>
              </div>
            )}
            
            <form onSubmit={handleLogin} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700">Email</label>
                <input
                  type="email"
                  required
                  value={loginForm.email}
                  onChange={(e) => setLoginForm({...loginForm, email: e.target.value})}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-emerald-500 focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Password</label>
                <input
                  type="password"
                  required
                  value={loginForm.password}
                  onChange={(e) => setLoginForm({...loginForm, password: e.target.value})}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-emerald-500 focus:border-emerald-500"
                />
              </div>

              <div>
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-emerald-600 hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500 disabled:opacity-50"
                >
                  {loading ? 'Signing in...' : 'Sign in'}
                </button>
              </div>
            </form>

            <div className="mt-6">
              <button
                onClick={() => setCurrentView('home')}
                className="w-full text-center text-sm text-emerald-600 hover:text-emerald-500"
              >
                ← Back to home
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Register Page
  if (currentView === 'register') {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
        <div className="sm:mx-auto sm:w-full sm:max-w-md">
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Create your account
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Or{' '}
            <button
              onClick={() => setCurrentView('login')}
              className="font-medium text-emerald-600 hover:text-emerald-500"
            >
              sign in to existing account
            </button>
          </p>
        </div>

        <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
          <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
            {error && (
              <div className="mb-4 bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded">
                {error}
                <button onClick={clearMessages} className="float-right text-red-400 hover:text-red-600">×</button>
              </div>
            )}
            
            <form onSubmit={handleRegister} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700">Full Name</label>
                <input
                  type="text"
                  required
                  value={registerForm.full_name}
                  onChange={(e) => setRegisterForm({...registerForm, full_name: e.target.value})}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-emerald-500 focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Email</label>
                <input
                  type="email"
                  required
                  value={registerForm.email}
                  onChange={(e) => setRegisterForm({...registerForm, email: e.target.value})}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-emerald-500 focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Phone (Optional)</label>
                <input
                  type="tel"
                  value={registerForm.phone}
                  onChange={(e) => setRegisterForm({...registerForm, phone: e.target.value})}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-emerald-500 focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Password</label>
                <input
                  type="password"
                  required
                  value={registerForm.password}
                  onChange={(e) => setRegisterForm({...registerForm, password: e.target.value})}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-emerald-500 focus:border-emerald-500"
                />
              </div>

              <div>
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-emerald-600 hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500 disabled:opacity-50"
                >
                  {loading ? 'Creating account...' : 'Create account'}
                </button>
              </div>
            </form>

            <div className="mt-6">
              <button
                onClick={() => setCurrentView('home')}
                className="w-full text-center text-sm text-emerald-600 hover:text-emerald-500"
              >
                ← Back to home
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Dashboard
  if (currentView === 'dashboard') {
    return (
      <div className="min-h-screen bg-gray-100">
        {/* Navigation */}
        <nav className="bg-white shadow">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex items-center">
                <h1 className="text-xl font-semibold text-gray-900">Dashboard</h1>
              </div>
              <div className="flex items-center space-x-4">
                <button
                  onClick={() => setCurrentView('courses')}
                  className="text-gray-500 hover:text-gray-700"
                >
                  All Courses
                </button>
                {user && ['admin', 'super_admin', 'instructor'].includes(user.role) && (
                  <button
                    onClick={() => setCurrentView('create-course')}
                    className="bg-emerald-600 text-white px-4 py-2 rounded-md hover:bg-emerald-700"
                  >
                    Create Course
                  </button>
                )}
                {user && ['admin', 'super_admin'].includes(user.role) && (
                  <button
                    onClick={() => setCurrentView('admin-panel')}
                    className="bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700"
                  >
                    Admin Panel
                  </button>
                )}
                <button
                  onClick={() => setCurrentView('home')}
                  className="text-gray-500 hover:text-gray-700"
                >
                  Home
                </button>
                <button
                  onClick={handleLogout}
                  className="bg-gray-600 text-white px-4 py-2 rounded-md hover:bg-gray-700"
                >
                  Logout
                </button>
              </div>
            </div>
          </div>
        </nav>

        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          {success && (
            <div className="mb-4 bg-green-50 border border-green-200 text-green-600 px-4 py-3 rounded">
              {success}
              <button onClick={clearMessages} className="float-right text-green-400 hover:text-green-600">×</button>
            </div>
          )}

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                Welcome back, {user?.full_name}!
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-emerald-50 p-4 rounded-lg">
                  <h4 className="font-medium text-emerald-800">Total Courses</h4>
                  <p className="text-2xl font-bold text-emerald-600">{courses.length}</p>
                </div>
                
                <div className="bg-blue-50 p-4 rounded-lg">
                  <h4 className="font-medium text-blue-800">Enrolled Courses</h4>
                  <p className="text-2xl font-bold text-blue-600">{user?.enrolled_courses?.length || 0}</p>
                </div>
                
                <div className="bg-purple-50 p-4 rounded-lg">
                  <h4 className="font-medium text-purple-800">Role</h4>
                  <p className="text-lg font-semibold text-purple-600 capitalize">{user?.role}</p>
                </div>
              </div>

              {user?.enrolled_courses?.length > 0 && (
                <div className="mt-8">
                  <h4 className="text-lg font-medium text-gray-900 mb-4">Your Enrolled Courses</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {courses
                      .filter(course => user.enrolled_courses.includes(course.id))
                      .map(course => (
                        <div key={course.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                          <h5 className="font-semibold text-gray-900">{course.title}</h5>
                          <p className="text-sm text-gray-600 mt-1">{course.instructor_name}</p>
                          <button
                            onClick={() => handleCourseView(course.id)}
                            className="mt-2 bg-emerald-600 text-white px-4 py-2 rounded text-sm hover:bg-emerald-700"
                          >
                            Continue Learning
                          </button>
                        </div>
                      ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // All Courses View
  if (currentView === 'courses') {
    return (
      <div className="min-h-screen bg-gray-100">
        {/* Navigation */}
        <nav className="bg-white shadow">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex items-center">
                <h1 className="text-xl font-semibold text-gray-900">All Courses</h1>
              </div>
              <div className="flex items-center space-x-4">
                <button
                  onClick={() => setCurrentView('dashboard')}
                  className="text-gray-500 hover:text-gray-700"
                >
                  Dashboard
                </button>
                <button
                  onClick={() => setCurrentView('home')}
                  className="text-gray-500 hover:text-gray-700"
                >
                  Home
                </button>
              </div>
            </div>
          </div>
        </nav>

        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {courses.map(course => (
              <div key={course.id} className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
                {course.thumbnail_url && (
                  <img
                    className="w-full h-48 object-cover"
                    src={course.thumbnail_url}
                    alt={course.title}
                  />
                )}
                <div className="p-6">
                  <div className="flex items-center justify-between mb-2">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      course.course_type === 'free' 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-blue-100 text-blue-800'
                    }`}>
                      {course.course_type === 'free' ? 'Free' : `৳${course.price}`}
                    </span>
                    <span className="text-sm text-gray-500">{course.student_count} students</span>
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">{course.title}</h3>
                  <p className="text-gray-600 text-sm mb-4">{course.description.substring(0, 100)}...</p>
                  <p className="text-sm text-gray-500 mb-4">Instructor: {course.instructor_name}</p>
                  <button
                    onClick={() => handleCourseView(course.id)}
                    className="w-full bg-emerald-600 text-white py-2 rounded-md hover:bg-emerald-700"
                  >
                    View Course
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // Course Detail View
  if (currentView === 'course-detail' && selectedCourse) {
    return (
      <div className="min-h-screen bg-gray-100">
        {/* Navigation */}
        <nav className="bg-white shadow">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex items-center">
                <button
                  onClick={() => setCurrentView('courses')}
                  className="text-emerald-600 hover:text-emerald-800 mr-4"
                >
                  ← Back to Courses
                </button>
                <h1 className="text-xl font-semibold text-gray-900">{selectedCourse.title}</h1>
              </div>
              <div className="flex items-center space-x-4">
                <button
                  onClick={() => setCurrentView('dashboard')}
                  className="text-gray-500 hover:text-gray-700"
                >
                  Dashboard
                </button>
              </div>
            </div>
          </div>
        </nav>

        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          {error && (
            <div className="mb-4 bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded">
              {error}
              <button onClick={clearMessages} className="float-right text-red-400 hover:text-red-600">×</button>
            </div>
          )}
          
          {success && (
            <div className="mb-4 bg-green-50 border border-green-200 text-green-600 px-4 py-3 rounded">
              {success}
              <button onClick={clearMessages} className="float-right text-green-400 hover:text-green-600">×</button>
            </div>
          )}

          <div className="bg-white shadow rounded-lg overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">{selectedCourse.title}</h2>
                  <p className="text-gray-600 mt-1">by {selectedCourse.instructor_name}</p>
                </div>
                <div className="text-right">
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                    selectedCourse.course_type === 'free' 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-blue-100 text-blue-800'
                  }`}>
                    {selectedCourse.course_type === 'free' ? 'Free Course' : `৳${selectedCourse.price}`}
                  </span>
                  {!selectedCourse.is_enrolled && selectedCourse.course_type !== 'free' && (
                    <div className="mt-2">
                      <button
                        onClick={() => handleEnrollment(selectedCourse.id)}
                        disabled={loading}
                        className="bg-emerald-600 text-white px-4 py-2 rounded-md hover:bg-emerald-700 disabled:opacity-50"
                      >
                        {loading ? 'Processing...' : 'Enroll Now'}
                      </button>
                    </div>
                  )}
                  {!selectedCourse.is_enrolled && selectedCourse.course_type === 'free' && (
                    <div className="mt-2">
                      <button
                        onClick={() => handleEnrollment(selectedCourse.id)}
                        disabled={loading}
                        className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 disabled:opacity-50"
                      >
                        {loading ? 'Enrolling...' : 'Enroll Free'}
                      </button>
                    </div>
                  )}
                </div>
              </div>
              <p className="text-gray-700 mt-4">{selectedCourse.description}</p>
            </div>

            <div className="px-6 py-4">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Course Content</h3>
                {user && ['admin', 'super_admin', 'instructor'].includes(user.role) && (
                  <div className="flex space-x-2">
                    <button
                      onClick={() => setShowAddLesson(true)}
                      className="bg-emerald-600 text-white px-4 py-2 rounded-md hover:bg-emerald-700 text-sm"
                    >
                      Add Lesson
                    </button>
                    <button
                      onClick={() => setShowLessonManagement(!showLessonManagement)}
                      className="bg-gray-600 text-white px-4 py-2 rounded-md hover:bg-gray-700 text-sm"
                    >
                      {showLessonManagement ? 'Hide Management' : 'Manage Lessons'}
                    </button>
                  </div>
                )}
              </div>

              {/* Add/Edit Lesson Form */}
              {showAddLesson && (
                <div className="mb-6 bg-gray-50 p-4 rounded-lg border">
                  <h4 className="text-md font-semibold text-gray-900 mb-4">
                    {editingLessonId ? 'Edit Lesson' : 'Add New Lesson'}
                  </h4>
                  <form onSubmit={handleAddLesson} className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Lesson Title</label>
                        <input
                          type="text"
                          required
                          value={lessonForm.title}
                          onChange={(e) => setLessonForm({...lessonForm, title: e.target.value})}
                          className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-emerald-500 focus:border-emerald-500"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Duration (minutes)</label>
                        <input
                          type="number"
                          min="1"
                          value={lessonForm.duration}
                          onChange={(e) => setLessonForm({...lessonForm, duration: e.target.value})}
                          className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-emerald-500 focus:border-emerald-500"
                        />
                      </div>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Description</label>
                      <textarea
                        required
                        rows={3}
                        value={lessonForm.description}
                        onChange={(e) => setLessonForm({...lessonForm, description: e.target.value})}
                        className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-emerald-500 focus:border-emerald-500"
                      />
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Video URL</label>
                        <input
                          type="url"
                          required
                          value={lessonForm.video_url}
                          onChange={(e) => setLessonForm({...lessonForm, video_url: e.target.value})}
                          placeholder="https://youtube.com/watch?v=... or https://vimeo.com/..."
                          className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-emerald-500 focus:border-emerald-500"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Video Type</label>
                        <select
                          value={lessonForm.video_type}
                          onChange={(e) => setLessonForm({...lessonForm, video_type: e.target.value})}
                          className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-emerald-500 focus:border-emerald-500"
                        >
                          <option value="youtube">YouTube</option>
                          <option value="vimeo">Vimeo</option>
                        </select>
                      </div>
                    </div>
                    
                    <div className="flex items-center">
                      <input
                        type="checkbox"
                        id="is_preview"
                        checked={lessonForm.is_preview}
                        onChange={(e) => setLessonForm({...lessonForm, is_preview: e.target.checked})}
                        className="h-4 w-4 text-emerald-600 focus:ring-emerald-500 border-gray-300 rounded"
                      />
                      <label htmlFor="is_preview" className="ml-2 block text-sm text-gray-700">
                        Make this a preview lesson (free for everyone)
                      </label>
                    </div>
                    
                    <div className="flex justify-end space-x-2">
                      <button
                        type="button"
                        onClick={() => {
                          setShowAddLesson(false);
                          setEditingLessonId(null);
                          setLessonForm({
                            title: '',
                            description: '',
                            video_url: '',
                            video_type: 'youtube',
                            duration: '',
                            is_preview: false
                          });
                        }}
                        className="bg-gray-600 text-white px-4 py-2 rounded-md hover:bg-gray-700"
                      >
                        Cancel
                      </button>
                      <button
                        type="submit"
                        disabled={loading}
                        className="bg-emerald-600 text-white px-4 py-2 rounded-md hover:bg-emerald-700 disabled:opacity-50"
                      >
                        {loading ? (editingLessonId ? 'Updating...' : 'Adding...') : (editingLessonId ? 'Update Lesson' : 'Add Lesson')}
                      </button>
                    </div>
                  </form>
                </div>
              )}

              {selectedCourse.lessons && selectedCourse.lessons.length > 0 ? (
                <div className="space-y-4">
                  {selectedCourse.lessons.map((lesson, index) => (
                    <div key={lesson.id} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-medium text-gray-900">
                          {index + 1}. {lesson.title}
                        </h4>
                        <div className="flex items-center space-x-2">
                          {lesson.is_preview && (
                            <span className="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded">
                              Preview
                            </span>
                          )}
                          {lesson.duration && (
                            <span className="text-sm text-gray-500">{lesson.duration} min</span>
                          )}
                          {showLessonManagement && user && ['admin', 'super_admin', 'instructor'].includes(user.role) && (
                            <div className="flex space-x-1">
                              <button
                                onClick={() => {
                                  setEditingLessonId(lesson.id);
                                  setLessonForm({
                                    title: lesson.title,
                                    description: lesson.description,
                                    video_url: lesson.video_url,
                                    video_type: lesson.video_type,
                                    duration: lesson.duration?.toString() || '',
                                    is_preview: lesson.is_preview
                                  });
                                  setShowAddLesson(true);
                                }}
                                className="bg-blue-600 text-white px-2 py-1 rounded text-xs hover:bg-blue-700"
                              >
                                Edit
                              </button>
                              <button
                                onClick={() => handleDeleteLesson(lesson.id)}
                                className="bg-red-600 text-white px-2 py-1 rounded text-xs hover:bg-red-700"
                              >
                                Delete
                              </button>
                            </div>
                          )}
                        </div>
                      </div>
                      <p className="text-gray-600 text-sm mb-3">{lesson.description}</p>
                      
                      {(selectedCourse.is_enrolled || lesson.is_preview) && (
                        <div className="aspect-w-16 aspect-h-9">
                          <iframe
                            src={getVideoEmbedUrl(lesson.video_url, lesson.video_type)}
                            className="w-full h-64 rounded"
                            frameBorder="0"
                            allowFullScreen
                            title={lesson.title}
                          ></iframe>
                        </div>
                      )}
                      
                      {!selectedCourse.is_enrolled && !lesson.is_preview && (
                        <div className="bg-gray-100 p-4 rounded text-center">
                          <p className="text-gray-600">
                            {selectedCourse.course_type === 'free' 
                              ? 'Enroll in this free course to access this lesson'
                              : 'Purchase this course to access this lesson'
                            }
                          </p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500">No lessons available yet.</p>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Create Course View
  if (currentView === 'create-course') {
    return (
      <div className="min-h-screen bg-gray-100">
        {/* Navigation */}
        <nav className="bg-white shadow">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex items-center">
                <button
                  onClick={() => setCurrentView('dashboard')}
                  className="text-emerald-600 hover:text-emerald-800 mr-4"
                >
                  ← Back to Dashboard
                </button>
                <h1 className="text-xl font-semibold text-gray-900">Create New Course</h1>
              </div>
            </div>
          </div>
        </nav>

        <div className="max-w-3xl mx-auto py-6 sm:px-6 lg:px-8">
          {error && (
            <div className="mb-4 bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded">
              {error}
              <button onClick={clearMessages} className="float-right text-red-400 hover:text-red-600">×</button>
            </div>
          )}
          
          {success && (
            <div className="mb-4 bg-green-50 border border-green-200 text-green-600 px-4 py-3 rounded">
              {success}
              <button onClick={clearMessages} className="float-right text-green-400 hover:text-green-600">×</button>
            </div>
          )}

          <div className="bg-white shadow rounded-lg">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900">Course Information</h2>
            </div>
            
            <form onSubmit={handleCreateCourse} className="px-6 py-4 space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700">Course Title</label>
                <input
                  type="text"
                  required
                  value={courseForm.title}
                  onChange={(e) => setCourseForm({...courseForm, title: e.target.value})}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-emerald-500 focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Description</label>
                <textarea
                  required
                  rows={4}
                  value={courseForm.description}
                  onChange={(e) => setCourseForm({...courseForm, description: e.target.value})}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-emerald-500 focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Instructor Name</label>
                <input
                  type="text"
                  required
                  value={courseForm.instructor_name}
                  onChange={(e) => setCourseForm({...courseForm, instructor_name: e.target.value})}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-emerald-500 focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Course Type</label>
                <select
                  value={courseForm.course_type}
                  onChange={(e) => setCourseForm({...courseForm, course_type: e.target.value})}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-emerald-500 focus:border-emerald-500"
                >
                  <option value="free">Free</option>
                  <option value="paid">Paid</option>
                </select>
              </div>

              {courseForm.course_type === 'paid' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700">Price (BDT)</label>
                  <input
                    type="number"
                    min="0"
                    step="0.01"
                    value={courseForm.price}
                    onChange={(e) => setCourseForm({...courseForm, price: e.target.value})}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-emerald-500 focus:border-emerald-500"
                  />
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-gray-700">Thumbnail URL (Optional)</label>
                <input
                  type="url"
                  value={courseForm.thumbnail_url}
                  onChange={(e) => setCourseForm({...courseForm, thumbnail_url: e.target.value})}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-emerald-500 focus:border-emerald-500"
                />
              </div>

              <div className="flex justify-end">
                <button
                  type="submit"
                  disabled={loading}
                  className="bg-emerald-600 text-white px-6 py-2 rounded-md hover:bg-emerald-700 disabled:opacity-50"
                >
                  {loading ? 'Creating...' : 'Create Course'}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    );
  }

  // Admin Panel View
  if (currentView === 'admin-panel') {
    return (
      <div className="min-h-screen bg-gray-100">
        {/* Admin Navigation */}
        <nav className="bg-purple-800 shadow">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex items-center">
                <h1 className="text-xl font-semibold text-white">Admin Panel</h1>
              </div>
              <div className="flex items-center space-x-4">
                <button
                  onClick={() => setCurrentView('dashboard')}
                  className="text-purple-200 hover:text-white"
                >
                  Back to Dashboard
                </button>
                <button
                  onClick={handleLogout}
                  className="bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700"
                >
                  Logout
                </button>
              </div>
            </div>
          </div>
        </nav>

        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          {/* Admin Panel Navigation */}
          <div className="bg-white shadow rounded-lg mb-6">
            <div className="px-4 py-5 sm:p-6">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <button
                  onClick={() => {
                    setCurrentView('admin-dashboard');
                    fetchAdminDashboard();
                  }}
                  className="bg-blue-600 text-white p-4 rounded-lg hover:bg-blue-700 text-center"
                >
                  📊 Dashboard
                </button>
                <button
                  onClick={() => {
                    setCurrentView('admin-users');
                    fetchAdminUsers();
                  }}
                  className="bg-green-600 text-white p-4 rounded-lg hover:bg-green-700 text-center"
                >
                  👥 Users
                </button>
                <button
                  onClick={() => {
                    setCurrentView('admin-courses');
                    fetchAdminCourses();
                  }}
                  className="bg-emerald-600 text-white p-4 rounded-lg hover:bg-emerald-700 text-center"
                >
                  📚 Courses
                </button>
                <button
                  onClick={() => {
                    setCurrentView('admin-analytics');
                    fetchAdminAnalytics();
                  }}
                  className="bg-purple-600 text-white p-4 rounded-lg hover:bg-purple-700 text-center"
                >
                  📈 Analytics
                </button>
              </div>
            </div>
          </div>

          {/* Welcome Message */}
          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Welcome to Admin Panel</h2>
              <p className="text-gray-600">
                Manage your Islamic Institute platform from here. You can manage users, courses, 
                view analytics and monitor system performance.
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Admin Dashboard View
  if (currentView === 'admin-dashboard') {
    return (
      <div className="min-h-screen bg-gray-100">
        {/* Admin Navigation */}
        <nav className="bg-purple-800 shadow">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex items-center">
                <button
                  onClick={() => setCurrentView('admin-panel')}
                  className="text-purple-200 hover:text-white mr-4"
                >
                  ← Back to Admin Panel
                </button>
                <h1 className="text-xl font-semibold text-white">Admin Dashboard</h1>
              </div>
            </div>
          </div>
        </nav>

        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          {adminLoading ? (
            <div className="text-center">Loading...</div>
          ) : adminData.dashboard ? (
            <>
              {/* Stats Cards */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                <div className="bg-white overflow-hidden shadow rounded-lg">
                  <div className="p-5">
                    <div className="flex items-center">
                      <div className="flex-shrink-0">
                        <div className="w-8 h-8 bg-blue-500 rounded-md flex items-center justify-center">
                          <span className="text-white text-sm">📚</span>
                        </div>
                      </div>
                      <div className="ml-5 w-0 flex-1">
                        <dl>
                          <dt className="text-sm font-medium text-gray-500 truncate">Total Courses</dt>
                          <dd className="text-lg font-medium text-gray-900">{adminData.dashboard.total_courses}</dd>
                        </dl>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="bg-white overflow-hidden shadow rounded-lg">
                  <div className="p-5">
                    <div className="flex items-center">
                      <div className="flex-shrink-0">
                        <div className="w-8 h-8 bg-green-500 rounded-md flex items-center justify-center">
                          <span className="text-white text-sm">👨‍🎓</span>
                        </div>
                      </div>
                      <div className="ml-5 w-0 flex-1">
                        <dl>
                          <dt className="text-sm font-medium text-gray-500 truncate">Students</dt>
                          <dd className="text-lg font-medium text-gray-900">{adminData.dashboard.total_students}</dd>
                        </dl>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="bg-white overflow-hidden shadow rounded-lg">
                  <div className="p-5">
                    <div className="flex items-center">
                      <div className="flex-shrink-0">
                        <div className="w-8 h-8 bg-purple-500 rounded-md flex items-center justify-center">
                          <span className="text-white text-sm">👨‍🏫</span>
                        </div>
                      </div>
                      <div className="ml-5 w-0 flex-1">
                        <dl>
                          <dt className="text-sm font-medium text-gray-500 truncate">Instructors</dt>
                          <dd className="text-lg font-medium text-gray-900">{adminData.dashboard.total_instructors}</dd>
                        </dl>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="bg-white overflow-hidden shadow rounded-lg">
                  <div className="p-5">
                    <div className="flex items-center">
                      <div className="flex-shrink-0">
                        <div className="w-8 h-8 bg-emerald-500 rounded-md flex items-center justify-center">
                          <span className="text-white text-sm">✅</span>
                        </div>
                      </div>
                      <div className="ml-5 w-0 flex-1">
                        <dl>
                          <dt className="text-sm font-medium text-gray-500 truncate">Enrollments</dt>
                          <dd className="text-lg font-medium text-gray-900">{adminData.dashboard.total_enrollments}</dd>
                        </dl>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Course Performance */}
              <div className="bg-white shadow rounded-lg">
                <div className="px-4 py-5 sm:p-6">
                  <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">Course Performance</h3>
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Course</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Enrollments</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Revenue</th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {adminData.dashboard.course_stats?.slice(0, 10).map((course, index) => (
                          <tr key={index}>
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                              {course.title}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {course.enrollments}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              ৳{course.revenue.toFixed(2)}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </>
          ) : (
            <div className="text-center">No data available</div>
          )}
        </div>
      </div>
    );
  }

  // Admin Users Management View
  if (currentView === 'admin-users') {
    return (
      <div className="min-h-screen bg-gray-100">
        {/* Admin Navigation */}
        <nav className="bg-purple-800 shadow">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex items-center">
                <button
                  onClick={() => setCurrentView('admin-panel')}
                  className="text-purple-200 hover:text-white mr-4"
                >
                  ← Back to Admin Panel
                </button>
                <h1 className="text-xl font-semibold text-white">User Management</h1>
              </div>
            </div>
          </div>
        </nav>

        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          {error && (
            <div className="mb-4 bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded">
              {error}
              <button onClick={clearMessages} className="float-right text-red-400 hover:text-red-600">×</button>
            </div>
          )}
          
          {success && (
            <div className="mb-4 bg-green-50 border border-green-200 text-green-600 px-4 py-3 rounded">
              {success}
              <button onClick={clearMessages} className="float-right text-green-400 hover:text-green-600">×</button>
            </div>
          )}

          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">All Users</h3>
              {adminLoading ? (
                <div className="text-center">Loading users...</div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">User</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Role</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Enrollments</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {adminData.users.map((u) => (
                        <tr key={u.id}>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center">
                              <div>
                                <div className="text-sm font-medium text-gray-900">{u.full_name}</div>
                                <div className="text-sm text-gray-500">{u.email}</div>
                              </div>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <select
                              value={u.role}
                              onChange={(e) => handleUpdateUserRole(u.id, e.target.value)}
                              className="text-sm border border-gray-300 rounded px-2 py-1"
                              disabled={u.id === user?.id} // Can't change own role
                            >
                              <option value="student">Student</option>
                              <option value="instructor">Instructor</option>
                              {user?.role === 'super_admin' && <option value="admin">Admin</option>}
                            </select>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                              u.is_active 
                                ? 'bg-green-100 text-green-800' 
                                : 'bg-red-100 text-red-800'
                            }`}>
                              {u.is_active ? 'Active' : 'Inactive'}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {u.total_enrollments}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                            {u.id !== user?.id && (
                              <button
                                onClick={() => handleUpdateUserStatus(u.id, !u.is_active)}
                                className={`px-3 py-1 rounded text-xs ${
                                  u.is_active
                                    ? 'bg-red-600 text-white hover:bg-red-700'
                                    : 'bg-green-600 text-white hover:bg-green-700'
                                }`}
                              >
                                {u.is_active ? 'Deactivate' : 'Activate'}
                              </button>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Admin Courses Management View
  if (currentView === 'admin-courses') {
    return (
      <div className="min-h-screen bg-gray-100">
        {/* Admin Navigation */}
        <nav className="bg-purple-800 shadow">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex items-center">
                <button
                  onClick={() => setCurrentView('admin-panel')}
                  className="text-purple-200 hover:text-white mr-4"
                >
                  ← Back to Admin Panel
                </button>
                <h1 className="text-xl font-semibold text-white">Course Management</h1>
              </div>
            </div>
          </div>
        </nav>

        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          {error && (
            <div className="mb-4 bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded">
              {error}
              <button onClick={clearMessages} className="float-right text-red-400 hover:text-red-600">×</button>
            </div>
          )}
          
          {success && (
            <div className="mb-4 bg-green-50 border border-green-200 text-green-600 px-4 py-3 rounded">
              {success}
              <button onClick={clearMessages} className="float-right text-green-400 hover:text-green-600">×</button>
            </div>
          )}

          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg leading-6 font-medium text-gray-900">All Courses</h3>
                <button
                  onClick={() => setCurrentView('create-course')}
                  className="bg-emerald-600 text-white px-4 py-2 rounded-md hover:bg-emerald-700"
                >
                  Create New Course
                </button>
              </div>
              
              {adminLoading ? (
                <div className="text-center">Loading courses...</div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Course</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Lessons</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Enrollments</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Revenue</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {adminData.courses.map((course) => (
                        <tr key={course.id}>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div>
                              <div className="text-sm font-medium text-gray-900">{course.title}</div>
                              <div className="text-sm text-gray-500">by {course.instructor_name}</div>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                              course.course_type === 'free' 
                                ? 'bg-green-100 text-green-800' 
                                : 'bg-blue-100 text-blue-800'
                            }`}>
                              {course.course_type === 'free' ? 'Free' : `৳${course.price}`}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {course.lesson_count}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {course.total_enrollments}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            ৳{course.revenue.toFixed(2)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                              course.is_active 
                                ? 'bg-green-100 text-green-800' 
                                : 'bg-red-100 text-red-800'
                            }`}>
                              {course.is_active ? 'Active' : 'Inactive'}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                            <button
                              onClick={() => handleCourseView(course.id)}
                              className="bg-blue-600 text-white px-3 py-1 rounded text-xs hover:bg-blue-700"
                            >
                              View
                            </button>
                            {course.total_enrollments === 0 && (
                              <button
                                onClick={() => handleDeleteCourse(course.id)}
                                className="bg-red-600 text-white px-3 py-1 rounded text-xs hover:bg-red-700"
                              >
                                Delete
                              </button>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Admin Analytics View
  if (currentView === 'admin-analytics') {
    return (
      <div className="min-h-screen bg-gray-100">
        {/* Admin Navigation */}
        <nav className="bg-purple-800 shadow">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex items-center">
                <button
                  onClick={() => setCurrentView('admin-panel')}
                  className="text-purple-200 hover:text-white mr-4"
                >
                  ← Back to Admin Panel
                </button>
                <h1 className="text-xl font-semibold text-white">Analytics & Reports</h1>
              </div>
            </div>
          </div>
        </nav>

        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          {adminLoading ? (
            <div className="text-center">Loading analytics...</div>
          ) : adminData.analytics ? (
            <>
              {/* Course Type Distribution */}
              <div className="bg-white shadow rounded-lg mb-6">
                <div className="px-4 py-5 sm:p-6">
                  <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">Course Distribution</h3>
                  <div className="grid grid-cols-2 gap-6">
                    <div className="text-center">
                      <div className="text-3xl font-bold text-green-600">
                        {adminData.analytics.course_type_distribution.free_courses}
                      </div>
                      <div className="text-sm text-gray-500">Free Courses</div>
                    </div>
                    <div className="text-center">
                      <div className="text-3xl font-bold text-blue-600">
                        {adminData.analytics.course_type_distribution.paid_courses}
                      </div>
                      <div className="text-sm text-gray-500">Paid Courses</div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Monthly Enrollment Trends */}
              <div className="bg-white shadow rounded-lg mb-6">
                <div className="px-4 py-5 sm:p-6">
                  <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">Enrollment Trends (Last 6 Months)</h3>
                  <div className="space-y-3">
                    {adminData.analytics.monthly_trends.map((month, index) => (
                      <div key={index} className="flex items-center justify-between">
                        <span className="text-sm font-medium text-gray-700">
                          {month.month} {month.year}
                        </span>
                        <div className="flex items-center">
                          <div className="w-32 bg-gray-200 rounded-full h-2 mr-3">
                            <div 
                              className="bg-blue-600 h-2 rounded-full" 
                              style={{
                                width: `${Math.max((month.enrollments / Math.max(...adminData.analytics.monthly_trends.map(m => m.enrollments), 1)) * 100, 5)}%`
                              }}
                            ></div>
                          </div>
                          <span className="text-sm text-gray-600">{month.enrollments}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Top Performing Courses */}
              <div className="bg-white shadow rounded-lg">
                <div className="px-4 py-5 sm:p-6">
                  <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">Top Performing Courses</h3>
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Course</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Enrollments</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Revenue</th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {adminData.analytics.top_courses.map((course, index) => (
                          <tr key={index}>
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                              {course.title}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                                course.type === 'free' 
                                  ? 'bg-green-100 text-green-800' 
                                  : 'bg-blue-100 text-blue-800'
                              }`}>
                                {course.type}
                              </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {course.enrollments}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              ৳{course.revenue.toFixed(2)}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </>
          ) : (
            <div className="text-center">No analytics data available</div>
          )}
        </div>
      </div>
    );
  }

  return null;
}

export default App;