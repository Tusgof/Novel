"""ProviderRunner-compatible OpenRouter CLI shim.

Reads a prompt from stdin or a prompt file, calls OpenRouter chat completions,
and writes only the assistant message content to stdout. The script never logs
or prints bearer tokens. It can retry with the User-scope NOVEL_OPENROUTER_API on
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
    process_value = os.environ.get("NOVEL_OPENROUTER_API", "").strip()
    if process_value:
        candidates.append(KeyCandidate(process_value, "process"))
        seen.add(process_value)
    user_value = _read_user_env("NOVEL_OPENROUTER_API").strip()
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
    reasoning_disabled: bool = False,
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
    elif reasoning_disabled:
        payload["reasoning"] = {"enabled": False}
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
            text = text.replace(candidate.value, "<NOVEL_OPENROUTER_API>")
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
    reasoning_mode = parser.add_mutually_exclusive_group()
    reasoning_mode.add_argument("--reasoning-enabled", action="store_true")
    reasoning_mode.add_argument("--reasoning-disabled", action="store_true")
    parser.add_argument("--reasoning-exclude", action="store_true")
    parser.add_argument("--transient-retries", type=int, default=1)
    parser.add_argument("--retry-delay-seconds", type=float, default=1.0)
    return parser.parse_args(argv)


def _empty_response_detail(payload: dict[str, Any]) -> str:
    choices = payload.get("choices") or [{}]
    choice = choices[0] if isinstance(choices[0], dict) else {}
    usage = payload.get("usage", {})
    details = {
        "finish_reason": choice.get("finish_reason"),
        "native_finish_reason": choice.get("native_finish_reason"),
        "completion_tokens": usage.get("completion_tokens"),
    }
    rendered = ", ".join(f"{key}={value}" for key, value in details.items() if value is not None)
    return f" ({rendered})" if rendered else ""


def _empty_response_is_transient(payload: dict[str, Any]) -> bool:
    choices = payload.get("choices") or [{}]
    choice = choices[0] if isinstance(choices[0], dict) else {}
    return choice.get("finish_reason") not in {"length", "content_filter"}


def _is_transient_failure(status: int) -> bool:
    return status == 0 or status in {408, 429} or status >= 500


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if args.transient_retries < 0 or args.retry_delay_seconds < 0:
        print("OpenRouter shim error: retry settings must be non-negative.", file=sys.stderr)
        return 2
    prompt = _read_prompt(args).strip()
    if not prompt:
        print("OpenRouter shim error: empty prompt.", file=sys.stderr)
        return 2

    candidates = _key_candidates()
    if not candidates:
        print("OpenRouter shim error: NOVEL_OPENROUTER_API is not set in process or User environment.", file=sys.stderr)
        return 2

    last_error = ""
    started = time.perf_counter()
    for index, candidate in enumerate(candidates):
        use_next_key = False
        for attempt in range(args.transient_retries + 1):
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
                reasoning_disabled=args.reasoning_disabled,
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
                last_error = "OpenRouter returned an empty assistant message" + _empty_response_detail(payload) + "."
                transient = _empty_response_is_transient(payload)
            else:
                last_error = error or f"OpenRouter HTTP status {status}."
                transient = _is_transient_failure(status)

            if transient and attempt < args.transient_retries:
                if args.retry_delay_seconds:
                    time.sleep(args.retry_delay_seconds)
                continue

            # User changed the key while Codex was running; a stale process env key
            # often fails with 401. Retry the User-scope candidate once when present.
            use_next_key = status == 401 and index + 1 < len(candidates)
            break

        if use_next_key:
            continue
        break

    elapsed = time.perf_counter() - started
    print(f"OpenRouter shim error after {elapsed:.2f}s: {last_error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
