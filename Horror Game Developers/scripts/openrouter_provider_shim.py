"""ProviderRunner-compatible OpenRouter CLI shim.

Reads a prompt from stdin or a prompt file, calls OpenRouter chat completions,
and writes only the assistant message content to stdout. The script never logs
or prints bearer tokens. It can retry with the User-scope OPENROUTER_API_KEY on
Windows when the current process environment still contains a stale key.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_SYSTEM_PROMPT = "You are a careful novel translation pipeline worker. Return only the requested output."


@dataclass(frozen=True)
class KeyCandidate:
    value: str
    source: str


def _read_user_env(name: str) -> str:
    if os.name != "nt":
        return ""
    try:
        import winreg  # type: ignore

        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
            value, _kind = winreg.QueryValueEx(key, name)
            return str(value)
    except Exception:
        return ""


def _key_candidates() -> list[KeyCandidate]:
    candidates: list[KeyCandidate] = []
    seen: set[str] = set()
    process_value = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if process_value:
        candidates.append(KeyCandidate(process_value, "process"))
        seen.add(process_value)
    user_value = _read_user_env("OPENROUTER_API_KEY").strip()
    if user_value and user_value not in seen:
        candidates.append(KeyCandidate(user_value, "user"))
    return candidates


def _read_prompt(args: argparse.Namespace) -> str:
    if args.prompt_file:
        return Path(args.prompt_file).read_text(encoding="utf-8")
    if args.prompt:
        return args.prompt
    return sys.stdin.read()


def _request_once(
    *,
    api_key: str,
    model: str,
    prompt: str,
    system_prompt: str,
    max_tokens: int,
    temperature: float,
    timeout: int,
    reasoning_enabled: bool,
    reasoning_exclude: bool,
) -> tuple[int, dict[str, Any] | None, str]:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if reasoning_enabled:
        payload["reasoning"] = {
            "enabled": True,
            "exclude": reasoning_exclude,
        }
    request = urllib.request.Request(
        CHAT_URL,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://local.novel-pipeline.invalid",
            "X-OpenRouter-Title": "Novel Pipeline Provider Shim",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8", errors="replace")
            return response.status, json.loads(body), ""
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return exc.code, None, _safe_error_preview(body)
    except Exception as exc:  # noqa: BLE001 - CLI shim must convert transport failures to stderr.
        return 0, None, _safe_error_preview(str(exc))


def _safe_error_preview(value: str) -> str:
    text = value.replace("\r", " ").replace("\n", " ").strip()
    for candidate in _key_candidates():
        if candidate.value:
            text = text.replace(candidate.value, "<OPENROUTER_API_KEY>")
    return text[:1000]


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--model", required=True)
    parser.add_argument("--prompt", default="")
    parser.add_argument("--prompt-file", default="")
    parser.add_argument("--system-prompt", default=DEFAULT_SYSTEM_PROMPT)
    parser.add_argument("--max-tokens", type=int, default=4096)
    parser.add_argument("--temperature", type=float, default=0.1)
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--reasoning-enabled", action="store_true")
    parser.add_argument("--reasoning-exclude", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    prompt = _read_prompt(args).strip()
    if not prompt:
        print("OpenRouter shim error: empty prompt.", file=sys.stderr)
        return 2

    candidates = _key_candidates()
    if not candidates:
        print("OpenRouter shim error: OPENROUTER_API_KEY is not set in process or User environment.", file=sys.stderr)
        return 2

    last_error = ""
    started = time.perf_counter()
    for index, candidate in enumerate(candidates):
        status, payload, error = _request_once(
            api_key=candidate.value,
            model=args.model,
            prompt=prompt,
            system_prompt=args.system_prompt,
            max_tokens=args.max_tokens,
            temperature=args.temperature,
            timeout=args.timeout,
            reasoning_enabled=args.reasoning_enabled,
            reasoning_exclude=args.reasoning_exclude,
        )
        if payload is not None and status == 200:
            content = (
                payload.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
            )
            if content:
                sys.stdout.write(str(content).strip())
                return 0
            last_error = "OpenRouter returned an empty assistant message."
            continue

        last_error = error or f"OpenRouter HTTP status {status}."
        # User changed the key while Codex was running; a stale process env key
        # often fails with 401. Retry the User-scope candidate once when present.
        if status == 401 and index + 1 < len(candidates):
            continue
        break

    elapsed = time.perf_counter() - started
    print(f"OpenRouter shim error after {elapsed:.2f}s: {last_error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
