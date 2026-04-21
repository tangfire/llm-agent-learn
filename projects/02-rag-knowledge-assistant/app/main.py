from __future__ import annotations

from contextlib import asynccontextmanager
import logging
from time import perf_counter

from fastapi import FastAPI, Request

from app.api.routes import router
from app.core.config import Settings, settings
from app.core.errors import register_exception_handlers
from app.core.logging import setup_logging
from app.services.rag import RAGService

logger = logging.getLogger(__name__)


def create_app(app_settings: Settings | None = None) -> FastAPI:
    resolved_settings = app_settings or settings
    setup_logging(resolved_settings.log_level)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        logger.info("Starting app | name=%s", resolved_settings.app_name)
        app.state.settings = resolved_settings
        app.state.rag_service = RAGService(resolved_settings)
        try:
            yield
        finally:
            app.state.rag_service.close()
            logger.info("Stopped app | name=%s", resolved_settings.app_name)

    app = FastAPI(title=resolved_settings.app_name, version="0.2.0", lifespan=lifespan)
    register_exception_handlers(app)
    app.include_router(router)

    @app.middleware("http")
    async def log_request(request: Request, call_next):
        started_at = perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            duration_ms = (perf_counter() - started_at) * 1000
            logger.exception(
                "Request failed | method=%s | path=%s | duration_ms=%.2f",
                request.method,
                request.url.path,
                duration_ms,
            )
            raise

        duration_ms = (perf_counter() - started_at) * 1000
        logger.info(
            "Request completed | method=%s | path=%s | status_code=%s | duration_ms=%.2f",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        return response

    @app.get("/")
    def root() -> dict[str, str]:
        return {
            "message": "RAG knowledge assistant service is running.",
            "docs": "/docs",
        }

    return app


app = create_app()
