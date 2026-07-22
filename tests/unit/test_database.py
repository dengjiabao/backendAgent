from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import Mock

from ecommerce_agent.persistence import database


def test_initialize_postgres_enables_vector_extension_before_tables(monkeypatch):
    connection = Mock()

    @contextmanager
    def begin():
        yield connection

    engine = SimpleNamespace(dialect=SimpleNamespace(name="postgresql"), begin=begin)
    create_all = Mock()
    monkeypatch.setattr(database.Base.metadata, "create_all", create_all)

    database.initialize_database(engine)  # type: ignore[arg-type]

    connection.execute.assert_called_once()
    assert "CREATE EXTENSION IF NOT EXISTS vector" in str(connection.execute.call_args.args[0])
    create_all.assert_called_once_with(engine)
