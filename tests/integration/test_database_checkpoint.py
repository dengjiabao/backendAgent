import asyncio

from ecommerce_agent.agents.checkpoint import DatabaseRunCheckpoint
from ecommerce_agent.persistence.database import create_database_engine, create_session_factory, initialize_database


def test_database_checkpoint_persists_resume_state(tmp_path):
    engine = create_database_engine(f"sqlite+pysqlite:///{tmp_path / 'checkpoint.db'}")
    initialize_database(engine)
    checkpoint = DatabaseRunCheckpoint(create_session_factory(engine))
    checkpoint.save("thread-1", {"status": "waiting_approval", "approval_id": "a-1"})
    resumed = asyncio.run(checkpoint.resume("thread-1", {"status": "approved"}))
    assert resumed["approval_id"] == "a-1"
    assert checkpoint.load("thread-1")["status"] == "approved"
