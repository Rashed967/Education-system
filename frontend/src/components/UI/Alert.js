import React from 'react';

const Alert = ({ type, message, onClose }) => {
  if (!message) return null;

  const baseClasses = "px-4 py-3 rounded border mb-4";
  const typeClasses = {
    success: "bg-green-50 border-green-200 text-green-600",
    error: "bg-red-50 border-red-200 text-red-600",
    warning: "bg-yellow-50 border-yellow-200 text-yellow-600",
    info: "bg-blue-50 border-blue-200 text-blue-600"
  };

  return (
    <div className={`${baseClasses} ${typeClasses[type] || typeClasses.info}`}>
      {message}
      {onClose && (
        <button 
          onClick={onClose} 
          className="float-right ml-4 font-bold hover:opacity-70"
        >
          ×
        </button>
      )}
    </div>
  );
};

export default Alert;