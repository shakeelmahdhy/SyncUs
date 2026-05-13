"""
FastAPI entrypoint for SyncUs.

Load backend/.env before importing routers or modules that read os.environ.

Policy: never call supabase.create_client() at module import time in feature
code. Use app.core.supabase_client.get_supabase_service_client() (or
get_supabase_publishable_client()) inside functions so missing env or import
order cannot crash the app during startup discovery.
"""

from pathlib import Path

from dotenv import load_dotenv

_backend_root = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=_backend_root / ".env")

from fastapi import FastAPI
<<<<<<< HEAD

from app.api.router import api_router
=======
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
>>>>>>> dev

# Import module routers
from app.modules.jobs import router as jobs_router
from app.modules.accounts import router as accounts_router
from app.modules.matching import router as matching_router
from app.modules.tracking import router as tracking_router


<<<<<<< HEAD

@app.get("/")
def root():
    return {"message": "SyncUs API running 🚀"}
=======
# Application metadata
app = FastAPI(
    title="SyncUs API",
    description="Intelligent Job Matching Platform",
    version="1.0.0",
    docs_url="/api/docs"
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
@app.get("/")
async def root():
    return {
        "message": "Welcome to SyncUs API",
        "docs": "/api/docs",
        "health": "/health"
    }


# Include module routers
app.include_router(jobs_router)
app.include_router(accounts_router)
app.include_router(matching_router)
app.include_router(tracking_router)



@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc) if os.getenv("DEBUG") == "true" else "An error occurred"
        }
    )



if __name__ == "__main__":
    import uvicorn

    # Run the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
>>>>>>> dev
