import React from 'react';
import { getVideoEmbedUrl } from '../../utils/helpers';

const VideoPlayer = ({ lesson, className = '' }) => {
  const embedUrl = getVideoEmbedUrl(lesson.video_url, lesson.video_type);

  return (
    <div className={`video-wrapper ${className}`}>
      <div className="aspect-w-16 aspect-h-9">
        <iframe
          src={embedUrl}
          className="w-full h-64 rounded"
          frameBorder="0"
          allowFullScreen
          title={lesson.title}
        ></iframe>
      </div>
    </div>
  );
};

export default VideoPlayer;