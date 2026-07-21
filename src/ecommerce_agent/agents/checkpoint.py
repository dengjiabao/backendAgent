from copy import deepcopy
from typing import Any, Protocol


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
