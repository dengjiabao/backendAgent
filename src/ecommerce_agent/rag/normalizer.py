import re


def normalize_markdown(text: str) -> str:
    text = text.replace("\r\n", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    lines = [line.rstrip() for line in text.splitlines()]
    result: list[str] = []
    previous = None
    for line in lines:
        if line and line == previous and not line.startswith("#"):
            continue
        result.append(line)
        previous = line
    return "\n".join(result).strip() + "\n"
