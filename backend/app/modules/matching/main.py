from fastapi import FastAPI
from app.modules.matching.router import router as matching_router

app = FastAPI()

# Register matching module
app.include_router(matching_router, prefix="/matching")
