from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app


def test_health() -> None:
    with TestClient(create_app(Settings(_env_file=None))) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "AI Task & Document Assistant",
    }


def test_configured_service_name() -> None:
    settings = Settings(_env_file=None, app_name="Local Test Service")
    with TestClient(create_app(settings)) as client:
        assert client.get("/health").json()["service"] == settings.app_name
        assert client.get("/openapi.json").json()["info"]["title"] == settings.app_name
        response = client.get("/docs")
    assert response.status_code == 200
    assert "swagger-ui" in response.text
