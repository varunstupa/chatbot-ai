"""FastAPI application entrypoint."""

from __future__ import annotations

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.config.settings import get_settings
from app.utils.logger import configure_logging, get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    s = get_settings()
    logger.info(
        "startup | %s v%s | listen %s:%s",
        s.app.name,
        s.app.version,
        s.server.host,
        s.server.port,
    )
    yield
    logger.info("shutdown")


def create_app() -> FastAPI:
    s = get_settings()
    configure_logging(s)
    application = FastAPI(
        title=s.app.name,
        version=s.app.version,
        lifespan=lifespan,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:4200",
            "http://127.0.0.1:4200",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(router)
    # Same routes under /api for SPAs and proxies (e.g. /api/query/stream).
    application.include_router(router, prefix="/api")
    return application


app = create_app()


def main() -> None:
    s = get_settings()
    uvicorn.run(
        "app.main:app",
        host=s.server.host,
        port=s.server.port,
        reload=False,
    )


if __name__ == "__main__":
    main()
