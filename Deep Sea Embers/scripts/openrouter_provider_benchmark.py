"""Benchmark OpenRouter models for translation-pipeline provider roles.

This script is intentionally separate from production pipeline execution. It
reads fixtures from the workspace, calls OpenRouter, and writes experiment
artifacts only under 04_Work/_experiments plus a markdown report in 07_Reports.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT_ROOT = PROJECT_ROOT / "04_Work" / "_experiments"
REPORT_ROOT = PROJECT_ROOT / "07_Reports"
OPENROUTER_CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"

DEFAULT_MODELS = [
    "deepseek/deepseek-v4-flash",
    "tencent/hy3-preview",
    "minimax/minimax-m3",
    "minimax/minimax-m3",
    "xiaomi/mimo-v2.5",
    "openrouter/owl-alpha",
    "anthropic/claude-sonnet-4.6",
    "deepseek/deepseek-v4-pro",
    "deepseek/deepseek-v3.2",
    "google/gemini-3-flash-preview",
]

ROLE_ORDER = ("smoke", "glossary", "literal", "refine", "qa", "format")


@dataclass(frozen=True)
class Task:
    role: str
    prompt: str
    max_tokens: int


def _now_id() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _strip_code_fence(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```[a-zA-Z0-9_-]*\s*", "", stripped)
        stripped = re.sub(r"\s*```$", "", stripped)
    return stripped.strip()


def _safe_write_json(path: Path, data: Any) -> None:
    text = json.dumps(data, ensure_ascii=False, indent=2)
    if os.environ.get("OPENROUTER_API_KEY") and os.environ["OPENROUTER_API_KEY"] in text:
        raise RuntimeError(f"Refusing to write API key to {path}")
    path.write_text(text + "\n", encoding="utf-8")


def _safe_write_text(path: Path, text: str) -> None:
    if os.environ.get("OPENROUTER_API_KEY") and os.environ["OPENROUTER_API_KEY"] in text:
        raise RuntimeError(f"Refusing to write API key to {path}")
    path.write_text(text, encoding="utf-8")


def _post_openrouter(api_key: str, model: str, prompt: str, max_tokens: int, timeout: int) -> dict[str, Any]:
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are a careful benchmark worker. Follow the requested output format exactly.",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.1,
        "max_tokens": max_tokens,
    }
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        OPENROUTER_CHAT_URL,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://local.novel-pipeline.invalid",
            "X-OpenRouter-Title": "Novel Pipeline Provider Benchmark",
        },
    )
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8", errors="replace")
            elapsed = time.perf_counter() - started
            parsed = json.loads(raw)
            message = parsed.get("choices", [{}])[0].get("message", {})
            return {
                "ok": True,
                "status": response.status,
                "latency_seconds": round(elapsed, 3),
                "model": model,
                "returned_model": parsed.get("model"),
                "content": message.get("content", ""),
                "usage": parsed.get("usage", {}),
                "finish_reason": parsed.get("choices", [{}])[0].get("finish_reason"),
            }
    except urllib.error.HTTPError as exc:
        elapsed = time.perf_counter() - started
        error_body = exc.read().decode("utf-8", errors="replace")[:1000]
        return {
            "ok": False,
            "status": exc.code,
            "latency_seconds": round(elapsed, 3),
            "model": model,
            "error": "http_error",
            "error_preview": error_body,
        }
    except Exception as exc:  # noqa: BLE001 - benchmark should classify all transport failures.
        elapsed = time.perf_counter() - started
        return {
            "ok": False,
            "status": None,
            "latency_seconds": round(elapsed, 3),
            "model": model,
            "error": type(exc).__name__,
            "error_preview": str(exc)[:1000],
        }


def _fetch_model_catalog(timeout: int) -> dict[str, Any]:
    with urllib.request.urlopen(OPENROUTER_MODELS_URL, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return {item["id"]: item for item in payload.get("data", [])}


def _source_excerpt(chapter: str, limit: int = 2400) -> str:
    data = _read_json(PROJECT_ROOT / "03_Raw" / chapter / "source.json")
    return str(data.get("raw_text", ""))[:limit]


def _literal_fixture(block: str = "ch025-block-002") -> tuple[str, str]:
    chapter = block.split("-block-")[0]
    data = _read_json(PROJECT_ROOT / "04_Work" / chapter / f"{block}.literal.json")
    pairs = data.get("sentence_pairs", [])
    source = "\n".join(str(item.get("source_sentence", "")) for item in pairs)[:1800]
    literal = "\n\n".join(str(item.get("literal_sentence", "")) for item in pairs)[:2500]
    return source, literal


def _refined_fixture(block: str = "ch025-block-005") -> str:
    chapter = block.split("-block-")[0]
    data = _read_json(PROJECT_ROOT / "04_Work" / chapter / f"{block}.refined.json")
    return str(data.get("refined_text", ""))[:2500]


def build_tasks(roles: set[str]) -> list[Task]:
    tasks: list[Task] = []
    if "smoke" in roles:
        tasks.append(
            Task(
                "smoke",
                'ตอบกลับเป็น JSON เท่านั้น: {"ok": true, "thai": "พร้อม"}',
                80,
            )
        )
    if "glossary" in roles:
        excerpt = _source_excerpt("ch028", limit=2200)
        tasks.append(
            Task(
                "glossary",
                (
                    "Extract glossary-worthy Chinese terms from this novel excerpt. "
                    "Return JSON only with key candidates, each item has original_term, category, reason. "
                    "Prefer proper names, lore terms, organizations, artifacts. Reject generic words/fragments.\n\n"
                    f"EXCERPT:\n{excerpt}"
                ),
                700,
            )
        )
    if "literal" in roles:
        source, _literal = _literal_fixture("ch025-block-002")
        tasks.append(
            Task(
                "literal",
                (
                    "Translate Chinese to Thai literally and completely. Return JSON only: "
                    '{"literal_text": "...", "notes": []}. Preserve all meaning and quotation marks.\n\n'
                    f"SOURCE:\n{source}"
                ),
                1200,
            )
        )
    if "refine" in roles:
        source, literal = _literal_fixture("ch025-block-002")
        tasks.append(
            Task(
                "refine",
                (
                    "Refine this Thai literal translation into natural Thai novel prose without omitting, adding, "
                    "or changing viewpoint. Return refined Thai text only, no commentary.\n\n"
                    f"CHINESE SOURCE:\n{source}\n\nTHAI LITERAL:\n{literal}"
                ),
                1400,
            )
        )
    if "qa" in roles:
        source, literal = _literal_fixture("ch025-block-002")
        bad_refined = (
            "ระหว่างเขากับนกพิราบมีความเชื่อมโยงบางอย่างอยู่ และเมื่อกระตุ้นเปลวไฟแห่งร่างวิญญาณ "
            "ความเชื่อมโยงนั้นจะชัดเจนขึ้น ถึงขั้นที่เขาควบคุมได้ในระดับหนึ่งว่ามันจะไปปรากฏตรงไหน"
        )
        tasks.append(
            Task(
                "qa",
                (
                    "Judge whether the refined Thai preserves the Chinese source and literal Thai. "
                    "Return JSON only with keys passed(boolean), findings(array), feedback(string). "
                    "This fixture contains a known perspective drift if first-person thought becomes third-person.\n\n"
                    f"CHINESE SOURCE:\n{source}\n\nLITERAL:\n{literal}\n\nREFINED:\n{bad_refined}"
                ),
                900,
            )
        )
    if "format" in roles:
        refined = _refined_fixture("ch025-block-005")
        tasks.append(
            Task(
                "format",
                (
                    "Format this Thai novel text only. Preserve every word and sentence. "
                    "Do not summarize, rewrite, shorten, or add commentary. Return formatted Thai text only.\n\n"
                    f"TEXT:\n{refined}"
                ),
                1400,
            )
        )
    return tasks


def score_result(role: str, result: dict[str, Any]) -> dict[str, Any]:
    content = result.get("content", "") or ""
    stripped = _strip_code_fence(content)
    checks = {
        "nonempty": bool(stripped),
        "no_han_for_thai_roles": True,
        "json_valid_when_required": True,
        "qa_known_bad_caught": True,
        "format_not_truncated": True,
    }
    if role in {"smoke", "glossary", "literal", "qa"}:
        try:
            json.loads(stripped)
        except json.JSONDecodeError:
            checks["json_valid_when_required"] = False
    if role in {"literal", "refine", "format"}:
        checks["no_han_for_thai_roles"] = not bool(re.search(r"[\u4e00-\u9fff]", stripped))
    if role == "qa":
        try:
            parsed = json.loads(stripped)
            feedback = json.dumps(parsed, ensure_ascii=False).lower()
            checks["qa_known_bad_caught"] = parsed.get("passed") is False and (
                "perspective" in feedback or "มุมมอง" in feedback or "บุรุษ" in feedback
            )
        except json.JSONDecodeError:
            checks["qa_known_bad_caught"] = False
    if role == "format":
        source_len = len(_refined_fixture("ch025-block-005"))
        checks["format_not_truncated"] = len(stripped) >= int(source_len * 0.9)
    hard_fail = not result.get("ok") or not all(checks.values())
    score = 0
    if result.get("ok"):
        score += 20
    if checks["nonempty"]:
        score += 10
    if checks["json_valid_when_required"]:
        score += 15
    if checks["no_han_for_thai_roles"]:
        score += 15
    if checks["qa_known_bad_caught"]:
        score += 20
    if checks["format_not_truncated"]:
        score += 20
    return {"score": score, "hard_fail": hard_fail, "checks": checks}


def estimate_cost(model_info: dict[str, Any] | None, usage: dict[str, Any]) -> float | None:
    if not model_info:
        return None
    pricing = model_info.get("pricing") or {}
    try:
        prompt_price = float(pricing.get("prompt") or 0)
        completion_price = float(pricing.get("completion") or 0)
        prompt_tokens = int(usage.get("prompt_tokens") or 0)
        completion_tokens = int(usage.get("completion_tokens") or 0)
    except (TypeError, ValueError):
        return None
    return prompt_tokens * prompt_price + completion_tokens * completion_price


def summarize(results: list[dict[str, Any]]) -> list[str]:
    by_model: dict[str, list[dict[str, Any]]] = {}
    for item in results:
        by_model.setdefault(item["model"], []).append(item)
    lines = [
        "# OpenRouter Provider Benchmark Report",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "## Summary",
        "",
        "| Model | Calls | Hard fails | Avg score | Avg latency | Recommendation |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for model, items in by_model.items():
        calls = len(items)
        hard = sum(1 for item in items if item["score"]["hard_fail"])
        avg_score = sum(item["score"]["score"] for item in items) / calls if calls else 0
        avg_latency = sum(float(item["result"].get("latency_seconds") or 0) for item in items) / calls if calls else 0
        if hard == 0 and avg_score >= 85:
            rec = "candidate"
        elif hard == 0 and avg_score >= 75:
            rec = "fallback-only"
        else:
            rec = "reject or retest"
        lines.append(f"| `{model}` | {calls} | {hard} | {avg_score:.1f} | {avg_latency:.2f}s | {rec} |")
    lines.extend(["", "## Per-Task Results", ""])
    lines.append("| Model | Role | OK | Score | Hard fail | Latency | Notes |")
    lines.append("| --- | --- | --- | ---: | --- | ---: | --- |")
    for item in results:
        result = item["result"]
        score = item["score"]
        notes = []
        if not result.get("ok"):
            notes.append(str(result.get("error") or result.get("status")))
        for check, passed in score["checks"].items():
            if not passed:
                notes.append(check)
        cost = item.get("estimated_cost")
        if cost is not None:
            notes.append(f"est_cost={cost:.8f}")
        lines.append(
            f"| `{item['model']}` | {item['role']} | {result.get('ok')} | {score['score']} | "
            f"{score['hard_fail']} | {result.get('latency_seconds', 0)} | {', '.join(notes) or 'ok'} |"
        )
    lines.extend(
        [
            "",
            "## Safety",
            "",
            "- API key was read from `OPENROUTER_API_KEY` only.",
            "- No production ledger, glossary, source, work chapter artifacts, outputs, or provider config are edited by this script.",
            "- Raw responses are stored under the experiment directory for review.",
        ]
    )
    return lines


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke-only", action="store_true")
    parser.add_argument("--models", default=",".join(DEFAULT_MODELS))
    parser.add_argument("--roles", default=",".join(ROLE_ORDER))
    parser.add_argument("--max-calls", type=int, default=999)
    parser.add_argument("--timeout", type=int, default=120)
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("OPENROUTER_API_KEY is not set.", file=sys.stderr)
        return 2
    models = [item.strip() for item in args.models.split(",") if item.strip()]
    roles = {item.strip() for item in args.roles.split(",") if item.strip()}
    if args.smoke_only:
        roles = {"smoke"}
    invalid = roles - set(ROLE_ORDER)
    if invalid:
        raise SystemExit(f"Invalid roles: {sorted(invalid)}")

    run_id = f"openrouter_provider_benchmark_{_now_id()}"
    out_dir = EXPERIMENT_ROOT / run_id
    out_dir.mkdir(parents=True, exist_ok=False)
    REPORT_ROOT.mkdir(parents=True, exist_ok=True)

    catalog = _fetch_model_catalog(args.timeout)
    catalog_subset = {model: catalog.get(model) for model in models}
    _safe_write_json(out_dir / "model_catalog_subset.json", catalog_subset)

    tasks = build_tasks(roles)
    results: list[dict[str, Any]] = []
    call_count = 0
    for model in models:
        model_dir = out_dir / model.replace("/", "__").replace(":", "_")
        model_dir.mkdir(parents=True, exist_ok=True)
        for task in tasks:
            if call_count >= args.max_calls:
                break
            call_count += 1
            result = _post_openrouter(api_key, model, task.prompt, task.max_tokens, args.timeout)
            score = score_result(task.role, result)
            estimated = estimate_cost(catalog.get(model), result.get("usage") or {})
            record = {
                "model": model,
                "role": task.role,
                "result": result,
                "score": score,
                "estimated_cost": estimated,
            }
            results.append(record)
            _safe_write_json(model_dir / f"{task.role}.json", record)
        if call_count >= args.max_calls:
            break

    summary = {
        "run_id": run_id,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "models": models,
        "roles": sorted(roles),
        "call_count": call_count,
        "results": results,
    }
    _safe_write_json(out_dir / "benchmark_summary.json", summary)
    report_path = REPORT_ROOT / f"{run_id}.md"
    _safe_write_text(report_path, "\n".join(summarize(results)) + "\n")
    print(f"experiment_dir={out_dir}")
    print(f"report_path={report_path}")
    print(f"call_count={call_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
