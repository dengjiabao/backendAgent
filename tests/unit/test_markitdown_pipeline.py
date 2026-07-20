from ecommerce_agent.rag.chunker import chunk_markdown
from ecommerce_agent.rag.normalizer import normalize_markdown


def test_normalize_and_chunk_preserves_structure():
    text = "# 商品\n\n名称\n\n名称\n\n```java\nclass Demo {}\n```"
    chunks = chunk_markdown(normalize_markdown(text), "fixture.md")
    assert chunks
    assert chunks[0].heading_path == "商品"
    assert "class Demo" in chunks[0].content
