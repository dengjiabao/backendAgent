import re

_PATTERNS = [
    (re.compile(r"(?i)Authorization\s*:\s*Bearer\s+\S+"), "Authorization: [已脱敏]"),
    (re.compile(r"(?i)Cookie\s*:\s*\S+"), "Cookie: [已脱敏]"),
    (re.compile(r"(?i)(api[_-]?key)\s*[=:]\s*\S+"), r"\1=[已脱敏]"),
    (re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)"), "[手机号]"),
    (re.compile(r"地址\s*[:：]?\s*[^，,\n]+"), "地址：[地址]"),
]


def redact(text: str) -> str:
    """对日志、Prompt、Trace 和审计文本执行确定性脱敏。"""

    result = text
    for pattern, replacement in _PATTERNS:
        result = pattern.sub(replacement, result)
    return result
