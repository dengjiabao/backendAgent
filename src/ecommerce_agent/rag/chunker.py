import hashlib
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Chunk:
    id: str
    content: str
    heading_path: str
    source_uri: str


def chunk_markdown(text: str, source_uri: str, max_chars: int = 1200) -> list[Chunk]:
    heading = ""
    buffer: list[str] = []
    chunks: list[Chunk] = []

    def flush() -> None:
        content = "\n".join(buffer).strip()
        if not content:
            return
        for index in range(0, len(content), max_chars):
            part = content[index : index + max_chars]
            digest = hashlib.sha256(f"{source_uri}:{heading}:{part}".encode()).hexdigest()[:16]
            chunks.append(Chunk(digest, part, heading, source_uri))

    for line in text.splitlines():
        match = re.match(r"^(#{1,6})\s+(.+)$", line)
        if match:
            flush()
            buffer.clear()
            heading = match.group(2).strip()
        else:
            buffer.append(line)
    flush()
    return chunks
