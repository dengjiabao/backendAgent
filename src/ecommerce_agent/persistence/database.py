from pathlib import Path

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from ecommerce_agent.persistence.models import Base


def create_database_engine(url: str) -> Engine:
    if url.startswith("sqlite"):
        path = url.rsplit("///", 1)[-1]
        if path not in {":memory:", ""}:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
    return create_engine(url, pool_pre_ping=True)


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(engine, expire_on_commit=False)


def initialize_database(engine: Engine) -> None:
    if engine.dialect.name == "postgresql":
        with engine.begin() as connection:
            connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    Base.metadata.create_all(engine)
