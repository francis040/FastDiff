from pathlib import Path
from typing import Tuple

import chardet


def detect_encoding(path: Path) -> str:
    """Detect file encoding using chardet."""
    with path.open("rb") as f:
        raw = f.read()
    result = chardet.detect(raw)
    return result.get("encoding") or "utf-8"


def load_file(path: str) -> Tuple[str, str]:
    """Load a file and return its text along with detected encoding."""
    file_path = Path(path)
    encoding = detect_encoding(file_path)
    with file_path.open("r", encoding=encoding, errors="ignore") as f:
        content = f.read()
    return content, encoding
