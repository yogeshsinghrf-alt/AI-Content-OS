from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.history import router as history_router

from app.api.news import router as news_router
from app.api.ai import router as ai_router
from app.api.linkedin import router as linkedin_router
from app.api.social import router as social_router
from app.api.package import router as package_router
from app.api.image import router as image_router
from app.api.email import router as email_router
from app.api.export import router as export_router
from contextlib import asynccontextmanager
from app.api.scheduler import router as scheduler_router
from app.services.scheduler_service import (
    start_scheduler,
    stop_scheduler,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()

    yield

    stop_scheduler()
app = FastAPI(
    title="AI Content OS API",
    description="AI powered content intelligence platform",
    version="1.4.0",
    lifespan=lifespan,
)
app.include_router(
    export_router,
    prefix="/export",
    tags=["Export"]
)
app.include_router(
    history_router,
    prefix="/history"
)
app.include_router(
    scheduler_router,
    prefix="/scheduler",
    tags=["Scheduler"],
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(news_router, prefix="/news", tags=["News"])
app.include_router(ai_router, prefix="/ai", tags=["AI"])
app.include_router(linkedin_router, prefix="/linkedin", tags=["LinkedIn"])
app.include_router(social_router, prefix="/social", tags=["Social Media"])
app.include_router(package_router, prefix="/package", tags=["Daily Package"])
app.include_router(image_router,prefix="/image")
app.include_router(email_router, prefix="/email", tags=["Email"])

@app.get("/")
def home():
    return {
        "project": "AI Content OS",
        "version": "0.9.0",
        "status": "running"
    }