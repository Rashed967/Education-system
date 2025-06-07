import React from 'react';
import { formatCurrency, truncateText } from '../../utils/helpers';

const CourseCard = ({ course, onView, user }) => {
  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow course-card">
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
            {course.course_type === 'free' ? 'Free' : formatCurrency(course.price)}
          </span>
          {course.student_count > 0 && (
            <span className="text-sm text-gray-500">{course.student_count} students</span>
          )}
        </div>
        
        <h3 className="text-lg font-semibold text-gray-900 mb-2">{course.title}</h3>
        <p className="text-gray-600 text-sm mb-4">{truncateText(course.description, 100)}</p>
        <p className="text-sm text-gray-500 mb-4">Instructor: {course.instructor_name}</p>
        
        {course.total_duration && (
          <p className="text-sm text-gray-500 mb-4">Duration: {formatDuration(course.total_duration)}</p>
        )}
        
        <button
          onClick={() => user ? onView(course.id) : alert('Please login to view course details')}
          className="w-full bg-emerald-600 text-white py-2 rounded-md hover:bg-emerald-700 transition-colors"
        >
          View Course
        </button>
      </div>
    </div>
  );
};

export default CourseCard;