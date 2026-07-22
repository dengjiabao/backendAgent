from pathlib import Path


def test_minio_healthcheck_uses_builtin_http_endpoint():
    compose = Path("docker-compose.yml").read_text(encoding="utf-8")

    assert "minio/health/live" in compose
    assert '"mc", "ready", "local"' not in compose
