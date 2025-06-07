import React from 'react';

const Loading = ({ size = 'md', className = '' }) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12'
  };

  return (
    <div className={`flex justify-center items-center ${className}`}>
      <div className={`${sizeClasses[size]} border-4 border-emerald-200 border-t-emerald-600 rounded-full animate-spin`}></div>
    </div>
  );
};

export default Loading;