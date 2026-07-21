import re
from dataclasses import dataclass
from enum import StrEnum


class DocumentTrustLevel(StrEnum):
    TRUSTED = "trusted"
    INTERNAL = "internal"
    EXTERNAL = "external"


@dataclass(frozen=True)
class PromptSecurityFinding:
    blocked: bool
    trust: DocumentTrustLevel
    reasons: tuple[str, ...] = ()


class PromptInjectionDetector:
    """检测常见指令覆盖和敏感提示词窃取模式。"""

    _patterns = (
        re.compile(r"忽略.{0,12}(之前|以上).{0,8}指令"),
        re.compile(r"(输出|泄露|显示).{0,8}(系统提示词|system prompt)", re.IGNORECASE),
        re.compile(r"ignore.{0,12}(previous|above).{0,8}instructions", re.IGNORECASE),
    )

    def inspect(self, text: str, trust: DocumentTrustLevel) -> PromptSecurityFinding:
        reasons = tuple(pattern.pattern for pattern in self._patterns if pattern.search(text))
        return PromptSecurityFinding(bool(reasons), trust, reasons)
