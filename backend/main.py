from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import configuration
from config.settings import settings

# Import routes
from routes import auth_router, courses_router, admin_router

# Create FastAPI app
app = FastAPI(title=settings.app_name, debug=settings.debug)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": settings.app_name}

# Include routers
app.include_router(auth_router, prefix="/api")
app.include_router(courses_router, prefix="/api")  
app.include_router(admin_router, prefix="/api")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)