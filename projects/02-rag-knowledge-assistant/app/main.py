from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import close_services, router
from app.core.config import settings


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    close_services()


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
app.include_router(router)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "RAG knowledge assistant service is running.",
        "docs": "/docs",
    }
