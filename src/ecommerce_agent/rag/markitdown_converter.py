from pathlib import Path

from markitdown import MarkItDown


class MarkItDownConverter:
    def __init__(self, enable_plugins: bool = False) -> None:
        self.converter = MarkItDown(enable_plugins=enable_plugins)

    def convert(self, path: str | Path) -> str:
        return self.converter.convert(str(path)).text_content
