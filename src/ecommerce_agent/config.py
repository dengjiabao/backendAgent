import os
from typing import Any, Literal

from pydantic import BaseModel, SecretStr


class Settings(BaseModel):
    runtime_mode: Literal["standalone", "integrated"] = "standalone"
    commerce_adapter: str = "mock"
    model_base_url: str = "https://api.openai.com/v1"
    model_api_key: SecretStr | None = None
    model_name: str = "gpt-4o-mini"
    embedding_provider: Literal["hash", "openai"] = "hash"
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536
    markitdown_enable_plugins: bool = False
    max_upload_bytes: int = 50 * 1024 * 1024
    litemall_base_url: str = "http://127.0.0.1:8080"
    litemall_username: str = ""
    litemall_password: SecretStr | None = None
    state_backend: Literal["memory", "database"] = "memory"
    database_url: str = "sqlite+pysqlite:///./data/ecommerce_agent.db"
    redis_url: str = "redis://127.0.0.1:6379/0"

    def __init__(self, _env_file: str | None = ".env", **data: Any) -> None:
        del _env_file
        env_data: dict[str, Any] = {
            "runtime_mode": os.getenv("RUNTIME_MODE", "standalone"),
            "commerce_adapter": os.getenv("COMMERCE_ADAPTER", "mock"),
            "model_base_url": os.getenv("MODEL_BASE_URL", "https://api.openai.com/v1"),
            "model_name": os.getenv("MODEL_NAME", "gpt-4o-mini"),
            "embedding_provider": os.getenv("EMBEDDING_PROVIDER", "hash"),
            "embedding_model": os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
            "embedding_dimensions": int(os.getenv("EMBEDDING_DIMENSIONS", "1536")),
            "markitdown_enable_plugins": os.getenv("MARKITDOWN_ENABLE_PLUGINS", "false").lower() == "true",
            "max_upload_bytes": int(os.getenv("MAX_UPLOAD_BYTES", str(50 * 1024 * 1024))),
            "litemall_base_url": os.getenv("LITEMALL_BASE_URL", "http://127.0.0.1:8080"),
            "litemall_username": os.getenv("LITEMALL_USERNAME", ""),
            "state_backend": os.getenv("STATE_BACKEND", "memory"),
            "database_url": os.getenv("DATABASE_URL", "sqlite+pysqlite:///./data/ecommerce_agent.db"),
            "redis_url": os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0"),
        }
        if api_key := os.getenv("MODEL_API_KEY"):
            env_data["model_api_key"] = SecretStr(api_key)
        if litemall_password := os.getenv("LITEMALL_PASSWORD"):
            env_data["litemall_password"] = SecretStr(litemall_password)
        env_data.update(data)
        super().__init__(**env_data)


settings = Settings()
