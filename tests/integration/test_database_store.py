from pathlib import Path

from ecommerce_agent.persistence.database import create_database_engine, create_session_factory, initialize_database
from ecommerce_agent.persistence.database_store import DatabaseStore


def test_database_store_persists_approval_and_audit(tmp_path: Path):
    engine = create_database_engine(f"sqlite+pysqlite:///{tmp_path / 'agent.db'}")
    initialize_database(engine)
    store = DatabaseStore(create_session_factory(engine))

    approval = store.create_approval("product.update", {"id": "p-100"}, "run-db-1")
    decided = store.decide_approval(approval.id, "approved", "tester")

    assert decided.status == "approved"
    assert store.approvals[approval.id].operator == "tester"
    assert [event.event for event in store.audit_events] == ["approval.proposed", "approval.approved"]
