from fastapi import APIRouter

from app.modules.accounts.router import router as accounts_router
from app.modules.jobs.router import router as jobs_router
from app.modules.matching.router import router as matching_router
from app.modules.tracking.router import router as tracking_router

api_router = APIRouter()

api_router.include_router(accounts_router, prefix="/accounts", tags=["Accounts"])
api_router.include_router(jobs_router, prefix="/jobs", tags=["Jobs"])
api_router.include_router(matching_router, prefix="/matching", tags=["Matching"])
api_router.include_router(tracking_router, prefix="/tracking", tags=["Tracking"])