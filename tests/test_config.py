from pathlib import Path

import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_dotenv_and_environment_override(tmp_path: Path, monkeypatch) -> None:
    dotenv = tmp_path / ".env"
    dotenv.write_text(
        "APP_NAME=From dotenv\nAPI_PORT=8123\nDEBUG=true\n", encoding="utf-8"
    )
    monkeypatch.setenv("APP_NAME", "From environment")
    monkeypatch.delenv("API_PORT", raising=False)
    monkeypatch.delenv("DEBUG", raising=False)
    settings = Settings(_env_file=dotenv)
    assert settings.app_name == "From environment"
    assert settings.api_port == 8123
    assert settings.debug is True


@pytest.mark.parametrize("port", [0, 65536, "invalid"])
def test_invalid_port_is_rejected(port) -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, api_port=port)


def test_example_configuration_without_llm_key() -> None:
    settings = Settings(_env_file=".env.example")
    assert settings.llm_api_key.get_secret_value() == ""
    assert settings.app_name == "AI Task & Document Assistant"
