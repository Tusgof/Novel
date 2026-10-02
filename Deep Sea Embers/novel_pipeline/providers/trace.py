"""Opt-in provider call tracing for bounded experiments.

Tracing is disabled unless a trace directory is supplied on the request or via
``NOVEL_PIPELINE_TRACE_DIR``. Full prompt/response text is intentionally kept
local to the experiment directory and is never printed to stdout.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def trace_dir_from_env() -> Path | None:
    value = os.environ.get("NOVEL_PIPELINE_TRACE_DIR", "").strip()
    return Path(value).expanduser().resolve() if value else None


def context_from_env() -> dict[str, Any]:
    raw = os.environ.get("NOVEL_PIPELINE_TRACE_CONTEXT", "").strip()
    if not raw:
        return {}
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        return {"context_parse_error": True}
    return dict(value) if isinstance(value, Mapping) else {"context": value}


def redact_secrets(value: str) -> str:
    text = str(value)
    for name, secret in os.environ.items():
        if secret and ("API" in name or "KEY" in name or "TOKEN" in name):
            text = text.replace(secret, f"<{name}>")
    text = re.sub(r"(?i)(bearer\s+)[A-Za-z0-9._~-]+", r"\1<REDACTED>", text)
    text = re.sub(r"https://openrouter\.ai/[^\s\"']+", "<OPENROUTER_URL>", text)
    text = re.sub(r"(?i)(user_id[^A-Za-z0-9]{1,8})[A-Za-z0-9_-]+", r"\1<REDACTED>", text)
    return text


def extract_system_prompt(extra_args: tuple[str, ...]) -> str:
    args = list(extra_args)
    for index, value in enumerate(args[:-1]):
        if value == "--system-prompt":
            return args[index + 1]
    return "You are a careful novel translation pipeline worker. Return only the requested output."


def write_provider_trace(
    *,
    trace_dir: Path | None,
    request: Any,
    response: Any,
    usage: Mapping[str, Any] | None = None,
    failure_kind: str = "",
    system_prompt: str | None = None,
) -> Path | None:
    directory = trace_dir or trace_dir_from_env()
    if directory is None:
        return None
    directory.mkdir(parents=True, exist_ok=True)
    prompt = redact_secrets(request.prompt)
    stdout = redact_secrets(response.stdout or "")
    stderr = redact_secrets(response.stderr or "")
    context = context_from_env()
    context.update(getattr(request, "trace_context", {}) or {})
    event = {
        "schema": "novel.provider-trace.v1",
        "trace_id": uuid.uuid4().hex,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "context": context,
        "provider": response.provider,
        "model": response.model,
        "stage": response.stage or request.stage,
        "request": {
            "system_prompt": system_prompt or extract_system_prompt(tuple(getattr(request, "extra_args", ()) or ())),
            "user_prompt": prompt,
            "user_prompt_sha256": _sha256(prompt),
            "user_prompt_chars": len(prompt),
        },
        "response": {
            "stdout": stdout,
            "stdout_sha256": _sha256(stdout),
            "stdout_chars": len(stdout),
            "stderr": stderr,
            "returncode": response.returncode,
            "failure_kind": failure_kind,
            "started_at": response.started_at,
            "finished_at": response.finished_at,
            "duration_seconds": response.duration_seconds,
            "usage": dict(usage or getattr(response, "usage", {}) or {}),
        },
        "command": ["<PROMPT VIA STDIN>" if arg == request.prompt else redact_secrets(arg) for arg in response.command],
        "capture": "full_prompt_and_response_local_only",
    }
    path = directory / f"{event['recorded_at'].replace(':', '').replace('.', '')}_{event['trace_id']}.json"
    path.write_text(json.dumps(event, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


__all__ = ["context_from_env", "extract_system_prompt", "redact_secrets", "trace_dir_from_env", "write_provider_trace"]
