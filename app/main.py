from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

#route to modules
# from app.modules.accounts import router as accounts_router
# from app.modules.jobs import router as jobs_router
# from app.modules.matching import router as matching_router
from app.modules.tracking import router as tracking_router

#global api version prefix 
API_PREFIX = "/syncus/v1"

#define api router that mount to specific modules
v1_router=APIRouter(prefix=API_PREFIX)
# v1_router.include_router(accounts_router,prefix="/accounts", tags=["accounts"])
# v1_router.include_router(jobs_router,prefix="/jobs", tags=["jobs"])
# v1_router.include_router(matching_router,prefix="/matching", tags=["matching"])
v1_router.include_router(tracking_router,prefix="/tracking", tags=["tracking"])

#define app metadata 
app=FastAPI(
    title="SyncUs API",
    version="1.0.0",
    description="API for SyncUs (accounts, jobs, matching, tracking modules)",
)

#define CORS policy to ensure frontend on vite can access the api
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#health check endpoint for monitoring
@app.get("/health")
async def health_check()->dict[str, str]:
    return {"status":"healthy"}




@app.get("/")
async def root ():
    return {"message":"Hello World"}

#register v1 router to main app
app.include_router(v1_router)

