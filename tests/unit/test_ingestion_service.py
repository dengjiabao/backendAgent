from pathlib import Path

import pytest

from ecommerce_agent.workers.ingestion import IngestionJobService


class FakeConverter:
    def __init__(self, markdown: str = "# 商品\n\n智能客服") -> None:
        self.markdown = markdown
        self.calls = 0

    def convert(self, path: str | Path) -> str:
        self.calls += 1
        return self.markdown


@pytest.mark.asyncio
async def test_ingestion_is_idempotent_for_same_source_hash(tmp_path: Path):
    source = tmp_path / "guide.md"
    source.write_text("原始文件", encoding="utf-8")
    converter = FakeConverter()
    service = IngestionJobService(converter=converter)

    first = await service.submit(source)
    second = await service.submit(source)

    assert first == second
    job = await service.run(first)
    assert job.status == "completed"
    assert len(job.chunks) == 1
    assert converter.calls == 1


@pytest.mark.asyncio
async def test_ingestion_retries_and_marks_failure(tmp_path: Path):
    source = tmp_path / "broken.md"
    source.write_text("原始文件", encoding="utf-8")

    class BrokenConverter(FakeConverter):
        def convert(self, path: str | Path) -> str:
            self.calls += 1
            raise RuntimeError("转换失败")

    service = IngestionJobService(converter=BrokenConverter(), max_retries=2)
    job_id = await service.submit(source)
    job = await service.run(job_id)

    assert job.status == "failed"
    assert job.attempts == 2
    assert "转换失败" in (job.error or "")
