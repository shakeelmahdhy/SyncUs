from fastapi import FastAPI
from modules.matching.router import router as matching_router

app = FastAPI()

# Register matching module
app.include_router(matching_router)