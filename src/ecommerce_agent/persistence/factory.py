from ecommerce_agent.config import Settings
from ecommerce_agent.persistence.database import create_database_engine, create_session_factory, initialize_database
from ecommerce_agent.persistence.database_store import DatabaseStore
from ecommerce_agent.persistence.store import InMemoryStore


def build_state_store(settings: Settings) -> InMemoryStore | DatabaseStore:
    if settings.state_backend == "memory":
        return InMemoryStore()
    engine = create_database_engine(settings.database_url)
    initialize_database(engine)
    return DatabaseStore(create_session_factory(engine))
