import pytest


def test_settings_default_to_standalone_mode(monkeypatch):
    monkeypatch.delenv("RUNTIME_MODE", raising=False)
    from ecommerce_agent.config import Settings

    settings = Settings(_env_file=None)
    assert settings.runtime_mode == "standalone"
    assert settings.commerce_adapter == "mock"


def test_production_rejects_development_jwt_secret(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.delenv("JWT_SECRET", raising=False)
    from ecommerce_agent.config import Settings

    with pytest.raises(ValueError, match="JWT_SECRET"):
        Settings(_env_file=None)
