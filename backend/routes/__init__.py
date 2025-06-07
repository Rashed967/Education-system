from .auth import router as auth_router
from .courses import router as courses_router
from .admin import router as admin_router

__all__ = ["auth_router", "courses_router", "admin_router"]