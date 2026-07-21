from collections.abc import Sequence


def compress_context(parts: Sequence[str], max_chars: int) -> str:
    """按证据顺序压缩上下文，不打乱来源优先级。"""

    if max_chars <= 0:
        return ""
    result: list[str] = []
    remaining = max_chars
    for part in parts:
        if remaining <= 0:
            break
        piece = part[:remaining]
        result.append(piece)
        remaining -= len(piece)
    return "\n\n".join(result)[:max_chars]
