"""FastAPI application factory."""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.models import init_db
from app.api.v1 import router as v1_router

settings = get_settings()
WEB_DIR = Path(__file__).resolve().parent.parent / "app" / "web"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    await init_db()
    yield
    # Shutdown


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API routes
    app.include_router(v1_router)

    # Health check
    @app.get("/health")
    async def health_check():
        return {"status": "ok", "version": settings.APP_VERSION}

    # Mount static files
    app.mount("/", StaticFiles(directory=str(WEB_DIR), html=True), name="static")

    return app


# Create the app instance
app = create_app()
