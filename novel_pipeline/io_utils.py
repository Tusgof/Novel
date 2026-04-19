from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from novel_pipeline.files import append_jsonl_line, atomic_write_text
from novel_pipeline.types import json_safe


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def write_text_atomic(path: Path, content: str) -> None:
    atomic_write_text(path, content)


def write_json_atomic(path: Path, payload: Any) -> None:
    atomic_write_text(path, json.dumps(json_safe(payload), ensure_ascii=False, indent=2) + "\n")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def append_jsonl(path: Path, payload: Any) -> None:
    append_jsonl_line(path, payload)


__all__ = [
    "append_jsonl",
    "read_json",
    "sha256_bytes",
    "sha256_text",
    "write_json_atomic",
    "write_text_atomic",
]
