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
    allow_origin_regex=r"^http://(\[::1\]|localhost|127\.0\.0\.1)(:\d+)?$",
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


app.include_router(api_router)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
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
    )
