from pathlib import Path

from ecommerce_agent.adapters.storage import FileObjectStore, MinioObjectStore
from ecommerce_agent.evaluation.rag import evaluate_retrieval
from ecommerce_agent.rag.context import compress_context
from ecommerce_agent.rag.query import rewrite_query
from ecommerce_agent.rag.reranker import KeywordReranker


def test_file_object_store_keeps_versioned_snapshot(tmp_path: Path):
    store = FileObjectStore(tmp_path)
    uri = store.put("docs/a.md", "# 版本一".encode())
    assert uri.endswith("docs/a.md")
    assert store.get(uri) == "# 版本一".encode()


def test_minio_object_store_adapter_keeps_storage_out_of_core():
    class Client:
        def __init__(self) -> None:
            self.data: dict[str, bytes] = {}

        def put_object(self, bucket, key, stream, length, content_type):
            self.data[f"{bucket}/{key}"] = stream.read(length)

        def get_object(self, bucket, key):
            import io

            return io.BytesIO(self.data[f"{bucket}/{key}"])

    adapter = MinioObjectStore(Client(), "knowledge")
    uri = adapter.put("raw/a.txt", b"data")
    assert adapter.get(uri) == b"data"


def test_query_rewrite_and_context_compression_are_deterministic():
    assert rewrite_query("请帮我查询订单状态") == "订单状态"
    compressed = compress_context(["第一段" * 20, "第二段"], max_chars=12)
    assert len(compressed) <= 12
    assert compressed.startswith("第一段")


def test_retrieval_evaluation_reports_recall_and_mrr():
    report = evaluate_retrieval(
        [{"expected_ids": ["a", "b"], "retrieved_ids": ["x", "b", "a"]}], top_k=3
    )
    assert report.recall_at_k == 1.0
    assert report.mrr == 0.5


def test_keyword_reranker_is_replaceable_by_model_reranker():
    first = type("Result", (), {"content": "订单状态 查询"})()
    second = type("Result", (), {"content": "商品说明"})()
    ranked = KeywordReranker().rerank("订单状态", [second, first])
    assert ranked[0] is first
