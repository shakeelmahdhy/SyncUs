from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os

# Import module routers
from app.modules.jobs import router as jobs_router



# Application metadata
app = FastAPI(
    title="SyncUs API",
    description="Intelligent Job Matching Platform - Backend API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React development server
        "http://localhost:5173",  # Vite development server
        os.getenv("FRONTEND_URL", "")  # Production frontend URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health", tags=["system"])
async def health_check():

    return {
        "status": "healthy",
        "service": "SyncUs Backend API",
        "version": "1.0.0"
    }


# Root endpoint
@app.get("/", tags=["system"])
async def root():

    return {
        "message": "Welcome to SyncUs API",
        "docs": "/api/docs",
        "health": "/health"
    }


# Include module routers
app.include_router(jobs_router)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled errors

    Args:
        request: FastAPI request
        exc: Exception

    Returns:
        JSON error response
    """
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc) if os.getenv("DEBUG") == "true" else "An error occurred"
        }
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    """
    Execute on application startup

    Initialize connections, load configurations, etc.
    """
    print("🚀 SyncUs Backend API starting up...")
    print(f"📝 API Documentation: http://localhost:8000/api/docs")
    print(f"🏥 Health Check: http://localhost:8000/health")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """
    Execute on application shutdown

    Clean up resources, close connections, etc.
    """
    print("👋 SyncUs Backend API shutting down...")


if __name__ == "__main__":
    import uvicorn

    # Run the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload for development
        log_level="info"
    )
