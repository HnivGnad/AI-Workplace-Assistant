"""Minimal FastAPI application and local server entry point."""

from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel

from app.core.config import Settings


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    service: str


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings if settings is not None else Settings()
    application = FastAPI(title=settings.app_name, debug=settings.debug)

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
