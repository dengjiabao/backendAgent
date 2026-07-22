import asyncio

from ecommerce_agent.agents.checkpoint import InMemoryRunCheckpoint


def test_checkpoint_saves_and_resumes_human_approval_state():
    checkpoint = InMemoryRunCheckpoint()
    checkpoint.save("thread-1", {"status": "waiting_approval", "approval_id": "a-1"})
    assert checkpoint.load("thread-1")["approval_id"] == "a-1"
    resumed = asyncio.run(checkpoint.resume("thread-1", {"status": "approved"}))
    assert resumed["status"] == "approved"
