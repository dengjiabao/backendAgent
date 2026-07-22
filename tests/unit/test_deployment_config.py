from pathlib import Path


def test_minio_healthcheck_uses_builtin_http_endpoint():
    compose = Path("docker-compose.yml").read_text(encoding="utf-8")

    assert "minio/health/live" in compose
    assert '"mc", "ready", "local"' not in compose


def test_worker_has_celery_healthcheck_instead_of_http_probe():
    compose = Path("docker-compose.yml").read_text(encoding="utf-8")

    worker_section = compose.split("  worker:\n", 1)[1]
    assert "healthcheck:" in worker_section
    assert "inspect ping" in worker_section
