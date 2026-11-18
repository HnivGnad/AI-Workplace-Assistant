"""Minimal FastAPI application and local server entry point."""

import logging
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from typing import Literal

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import sessionmaker
from starlette.responses import Response

from app.api.tasks import router as tasks_router
from app.core.config import Settings
from app.db.database import build_engine


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    service: str


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings if settings is not None else Settings()
    database_url = settings.database_url

    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        engine = build_engine(database_url)
        application.state.session_factory = sessionmaker(
            bind=engine, expire_on_commit=False
        )
        try:
            yield
        finally:
            engine.dispose()
            del application.state.session_factory

    application = FastAPI(
        title=settings.app_name, debug=settings.debug, lifespan=lifespan
    )

    @application.middleware("http")
    async def hide_server_errors(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        try:
            return await call_next(request)
        except Exception as exc:
            # Never expose SQL, connection details, or tracebacks, even in debug mode.
            logging.getLogger(__name__).error("Request failed: %s", type(exc).__name__)
            return JSONResponse(
                status_code=500, content={"detail": "Internal server error"}
            )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PATCH"],
        allow_headers=["Content-Type"],
    )
    application.include_router(tasks_router)

    @application.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(service=settings.app_name)

    return application


app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = Settings()
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        log_level=settings.log_level.lower(),
    )
