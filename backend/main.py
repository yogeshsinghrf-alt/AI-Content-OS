import os
import hmac

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.storage import (
    router as storage_router,
)
from app.api.company_news import (
    router as company_news_router,
)
from app.api.history import router as history_router
from app.api.news import router as news_router
from app.api.ai import router as ai_router
from app.api.linkedin import router as linkedin_router
from app.api.social import router as social_router
from app.api.package import router as package_router
from app.api.image import router as image_router
from app.api.email import router as email_router
from app.api.export import router as export_router
from app.api.scheduler import router as scheduler_router

from app.services.scheduler_service import (
    start_scheduler,
    stop_scheduler,
)


BACKEND_API_KEY = os.getenv(
    "BACKEND_API_KEY",
    "",
)

ENABLE_API_DOCS = (
    os.getenv(
        "ENABLE_API_DOCS",
        "false",
    ).lower()
    == "true"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()

    yield

    stop_scheduler()


app = FastAPI(
    title="AI Content OS API",
    description=(
        "AI powered content intelligence platform"
    ),
    version="1.4.0",
    lifespan=lifespan,
    docs_url=(
        "/docs"
        if ENABLE_API_DOCS
        else None
    ),
    redoc_url=(
        "/redoc"
        if ENABLE_API_DOCS
        else None
    ),
    openapi_url=(
        "/openapi.json"
        if ENABLE_API_DOCS
        else None
    ),
)


@app.middleware("http")
async def require_backend_api_key(
    request: Request,
    call_next,
):
    # Allow CORS preflight requests.
    if request.method == "OPTIONS":
        return await call_next(request)

    # Keep only the harmless service-status
    # root endpoint public.
    if request.url.path == "/":
        return await call_next(request)

    if not BACKEND_API_KEY:
        return JSONResponse(
            status_code=503,
            content={
                "detail":
                "Backend authentication is not configured."
            },
        )

    supplied_key = request.headers.get(
        "x-api-key",
        "",
    )

    if not supplied_key or not hmac.compare_digest(
        supplied_key,
        BACKEND_API_KEY,
    ):
        return JSONResponse(
            status_code=401,
            content={
                "detail": "Unauthorized"
            },
        )

    return await call_next(request)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://ai-content-os-lake.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    export_router,
    prefix="/export",
    tags=["Export"],
)

app.include_router(
    history_router,
    prefix="/history",
)

app.include_router(
    scheduler_router,
    prefix="/scheduler",
    tags=["Scheduler"],
)

app.include_router(
    news_router,
    prefix="/news",
    tags=["News"],
)

app.include_router(
    ai_router,
    prefix="/ai",
    tags=["AI"],
)

app.include_router(
    linkedin_router,
    prefix="/linkedin",
    tags=["LinkedIn"],
)

app.include_router(
    social_router,
    prefix="/social",
    tags=["Social Media"],
)

app.include_router(
    package_router,
    prefix="/package",
    tags=["Daily Package"],
)

app.include_router(
    image_router,
    prefix="/image",
)

app.include_router(
    email_router,
    prefix="/email",
    tags=["Email"],
)

app.include_router(
    storage_router,
    prefix="/storage",
    tags=["Storage"],
)
app.include_router(
    company_news_router,
    prefix="/package",
    tags=["Company Newsroom"],
)
@app.get("/")
def home():
    return {
        "project": "AI Content OS",
        "version": "0.9.0",
        "status": "running",
    }