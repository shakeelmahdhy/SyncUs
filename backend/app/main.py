"""
FastAPI entrypoint for SyncUs.

Load backend/.env before importing routers or modules that read os.environ.

Policy: never call supabase.create_client() at module import time in feature
code. Use app.core.supabase_client helpers inside request paths so missing env
cannot crash the app during startup discovery.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
<<<<<<< HEAD

_backend_root = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=_backend_root / ".env")

from app.api.router import api_router

app = FastAPI(
    title="SyncUs API",
    description="Intelligent Job Matching Platform",
    version="1.0.0",
    docs_url="/docs",
)

_frontend = os.getenv("FRONTEND_URL", "").strip()
_cors_origins = ["http://localhost:3000", "http://localhost:5173"]
if _frontend:
    _cors_origins.append(_frontend)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_origin_regex=r"^http://(localhost|127\.0\.0\.1):\d+$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["system"])
async def health_check():
    return {
        "status": "healthy",
        "service": "SyncUs Backend API",
        "version": "1.0.0",
    }


@app.get("/")
async def root():
    return {
        "message": "SyncUs API running",
        "docs": "/docs",
        "health": "/health",
    }

=======
import os

# Import module routers
from app.modules.jobs import router as jobs_router
>>>>>>> 28d9068 (Clean matching module branch for push)



<<<<<<< HEAD
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
=======
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
>>>>>>> 28d9068 (Clean matching module branch for push)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
<<<<<<< HEAD
            "error": str(exc) if os.getenv("DEBUG") == "true" else "An error occurred",
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
=======
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
>>>>>>> 28d9068 (Clean matching module branch for push)
    )
