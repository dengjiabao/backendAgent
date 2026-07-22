from copy import deepcopy
from datetime import UTC, datetime
from typing import Any, Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from ecommerce_agent.persistence.models import RunCheckpointRow


class RunCheckpointPort(Protocol):
    def save(self, thread_id: str, state: dict[str, Any]) -> None: ...
    def load(self, thread_id: str) -> dict[str, Any] | None: ...
    async def resume(self, thread_id: str, patch: dict[str, Any]) -> dict[str, Any]: ...


class InMemoryRunCheckpoint:
    """独立模式可恢复状态；生产环境可替换为 PostgreSQL Checkpointer。"""

    def __init__(self) -> None:
        self._states: dict[str, dict[str, Any]] = {}

    def save(self, thread_id: str, state: dict[str, Any]) -> None:
        self._states[thread_id] = deepcopy(state)

    def load(self, thread_id: str) -> dict[str, Any] | None:
        state = self._states.get(thread_id)
        return deepcopy(state) if state is not None else None

    async def resume(self, thread_id: str, patch: dict[str, Any]) -> dict[str, Any]:
        state = self.load(thread_id)
        if state is None:
            raise KeyError(thread_id)
        state.update(patch)
        self.save(thread_id, state)
        return state


class DatabaseRunCheckpoint:
    """PostgreSQL/SQLite 可用的持久化检查点实现。"""

    def __init__(self, sessions: sessionmaker[Session]) -> None:
        self.sessions = sessions

    def save(self, thread_id: str, state: dict[str, Any]) -> None:
        with self.sessions.begin() as session:
            row = session.get(RunCheckpointRow, thread_id)
            if row is None:
                session.add(RunCheckpointRow(thread_id=thread_id, state=deepcopy(state), updated_at=datetime.now(UTC)))
            else:
                row.state = deepcopy(state)
                row.updated_at = datetime.now(UTC)

    def load(self, thread_id: str) -> dict[str, Any] | None:
        with self.sessions() as session:
            row = session.scalar(select(RunCheckpointRow).where(RunCheckpointRow.thread_id == thread_id))
            return deepcopy(row.state) if row is not None else None

    async def resume(self, thread_id: str, patch: dict[str, Any]) -> dict[str, Any]:
        state = self.load(thread_id)
        if state is None:
            raise KeyError(thread_id)
        state.update(patch)
        self.save(thread_id, state)
        return state
