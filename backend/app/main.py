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

from app.api.router import api_router

app = FastAPI(title="SyncUs Backend")

app.include_router(api_router)


@app.get("/")
def root():
    return {"message": "SyncUs API running 🚀"}
