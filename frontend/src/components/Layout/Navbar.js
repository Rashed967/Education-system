import React from 'react';
import { useAuth } from '../../context/AuthContext';

const Navbar = ({ currentView, setCurrentView }) => {
  const { user, logout } = useAuth();

  return (
    <nav className="bg-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <button
                onClick={() => setCurrentView('home')}
                className="text-2xl font-bold text-emerald-600 hover:text-emerald-700"
              >
                Islamic Institute
              </button>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            {user ? (
              <>
                <span className="text-gray-700">Welcome, {user.full_name}</span>
                <button
                  onClick={() => setCurrentView('dashboard')}
                  className="text-emerald-600 hover:text-emerald-800"
                >
                  Dashboard
                </button>
                <button
                  onClick={() => setCurrentView('courses')}
                  className="text-gray-500 hover:text-gray-700"
                >
                  Courses
                </button>
                {user && ['admin', 'super_admin', 'instructor'].includes(user.role) && (
                  <button
                    onClick={() => setCurrentView('create-course')}
                    className="bg-emerald-600 text-white px-4 py-2 rounded-md hover:bg-emerald-700"
                  >
                    Create Course
                  </button>
                )}
                <button
                  onClick={logout}
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
  );
};

export default Navbar;