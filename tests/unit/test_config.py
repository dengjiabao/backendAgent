def test_settings_default_to_standalone_mode(monkeypatch):
    monkeypatch.delenv("RUNTIME_MODE", raising=False)
    from ecommerce_agent.config import Settings
    settings = Settings(_env_file=None)
    assert settings.runtime_mode == "standalone"
    assert settings.commerce_adapter == "mock"
