"""FastAPI application entrypoint."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.crawl import router as crawl_router
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
    from app.services.jira_service import JiraService

    ok, err = JiraService().validate_configuration()
    if ok:
        logger.info("startup | jira ticket creation configured")
    else:
        logger.warning(
            "startup | jira not configured (%s) — copy .env.example to .env "
            "and set JIRA_* variables",
            err,
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

    @application.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        logger.warning(
            "request_validation_failed | %s %s | errors=%s",
            request.method,
            request.url.path,
            exc.errors(),
        )
        return JSONResponse(
            status_code=422,
            content={
                "detail": exc.errors(),
                "code": "validation_error",
                "hint": (
                    "POST JSON with non-empty ``question`` (or ``message``) "
                    "and optional ``session_id``."
                ),
            },
        )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:4200",
            "http://127.0.0.1:4200",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Session-Id"],
    )
    application.include_router(router)
    application.include_router(crawl_router)
    # Same routes under /api for SPAs and proxies (e.g. /api/query/stream).
    application.include_router(router, prefix="/api")
    application.include_router(crawl_router, prefix="/api")
    return application


app = create_app()


def _uvicorn_reload_enabled() -> bool:
    """Auto-reload on file changes (dev only)."""
    flag = (os.environ.get("UVICORN_RELOAD") or "").strip().lower()
    if flag in ("1", "true", "yes"):
        return True
    env = (os.environ.get("APP_ENV") or "").strip().lower()
    return env == "development"


def main() -> None:
    s = get_settings()
    uvicorn.run(
        "app.main:app",
        host=s.server.host,
        port=s.server.port,
        reload=_uvicorn_reload_enabled(),
    )


if __name__ == "__main__":
    main()
