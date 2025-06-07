from typing import Dict, Any, List, Union

def convert_objectid_to_string(data: Union[Dict[Any, Any], List[Dict[Any, Any]]]) -> Union[Dict[Any, Any], List[Dict[Any, Any]]]:
    """Convert MongoDB ObjectId to string in data"""
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and '_id' in item:
                item['_id'] = str(item['_id'])
        return data
    elif isinstance(data, dict):
        if '_id' in data:
            data['_id'] = str(data['_id'])
        return data
    return data

def format_course_response(course: Dict[Any, Any], is_enrolled: bool = False) -> Dict[Any, Any]:
    """Format course response based on enrollment status"""
    course = convert_objectid_to_string(course)
    course['is_enrolled'] = is_enrolled
    
    # If not enrolled and course is paid, only show preview lessons
    if not is_enrolled and course.get("course_type") == "paid":
        course["lessons"] = [
            lesson for lesson in course.get("lessons", []) 
            if lesson.get("is_preview", False)
        ]
    
    return course

def extract_video_id(url: str, video_type: str) -> str:
    """Extract video ID from YouTube or Vimeo URL"""
    if video_type == 'youtube':
        import re
        match = re.search(r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)', url)
        return match.group(1) if match else ""
    elif video_type == 'vimeo':
        import re
        match = re.search(r'vimeo\.com\/(\d+)', url)
        return match.group(1) if match else ""
    return ""

def get_video_embed_url(url: str, video_type: str) -> str:
    """Get embeddable URL for video"""
    video_id = extract_video_id(url, video_type)
    if not video_id:
        return url
        
    if video_type == 'youtube':
        return f"https://www.youtube.com/embed/{video_id}"
    elif video_type == 'vimeo':
        return f"https://player.vimeo.com/video/{video_id}"
    
    return url