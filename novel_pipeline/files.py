from __future__ import annotations

import json
import os
import time
from contextlib import contextmanager
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, Iterator

from novel_pipeline.types import json_safe


def ensure_parent_dir(path: Path | str) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    return target


def atomic_write_text(path: Path | str, text: str, *, encoding: str = "utf-8") -> Path:
    target = ensure_parent_dir(path)
    with NamedTemporaryFile(
        mode="w",
        encoding=encoding,
        newline="\n",
        delete=False,
        dir=str(target.parent),
    ) as handle:
        handle.write(text)
        handle.flush()
        os.fsync(handle.fileno())
        temp_path = Path(handle.name)
    os.replace(temp_path, target)
    return target


def atomic_write_bytes(path: Path | str, data: bytes) -> Path:
    target = ensure_parent_dir(path)
    with NamedTemporaryFile(mode="wb", delete=False, dir=str(target.parent)) as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
        temp_path = Path(handle.name)
    os.replace(temp_path, target)
    return target


def atomic_write_json(
    path: Path | str,
    data: Any,
    *,
    indent: int = 2,
    sort_keys: bool = True,
) -> Path:
    payload = json.dumps(json_safe(data), ensure_ascii=False, indent=indent, sort_keys=sort_keys)
    return atomic_write_text(path, payload + "\n")


@contextmanager
def _exclusive_append_lock(path: Path, *, timeout_seconds: float = 30.0) -> Iterator[None]:
    lock_path = path.with_name(path.name + ".lock")
    ensure_parent_dir(lock_path)
    deadline = time.monotonic() + timeout_seconds
    with lock_path.open("a+b") as handle:
        handle.seek(0, os.SEEK_END)
        if handle.tell() == 0:
            handle.write(b"\0")
            handle.flush()
        while True:
            try:
                handle.seek(0)
                if os.name == "nt":
                    import msvcrt

                    msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl

                    fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except OSError:
                if time.monotonic() >= deadline:
                    raise TimeoutError(f"Timed out waiting for append lock: {lock_path}")
                time.sleep(0.01)
        try:
            yield
        finally:
            handle.seek(0)
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def append_jsonl_line(path: Path | str, record: Any) -> Path:
    target = ensure_parent_dir(path)
    if isinstance(record, str):
        line = record.rstrip("\n")
    else:
        line = json.dumps(json_safe(record), ensure_ascii=False, sort_keys=True)
    with _exclusive_append_lock(target):
        with target.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(line + "\n")
            handle.flush()
            os.fsync(handle.fileno())
    return target


def read_text_if_exists(path: Path | str, *, encoding: str = "utf-8") -> str | None:
    target = Path(path)
    if not target.exists():
        return None
    return target.read_text(encoding=encoding)


__all__ = [
    "append_jsonl_line",
    "atomic_write_bytes",
    "atomic_write_json",
    "atomic_write_text",
    "ensure_parent_dir",
    "read_text_if_exists",
]
