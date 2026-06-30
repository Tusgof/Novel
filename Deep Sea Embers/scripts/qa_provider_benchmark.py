"""Compare QA provider quality, latency, and cost on fixed non-production cases.

This benchmark does not touch production ledger, glossary notes, source files,
chapter work artifacts, final outputs, or provider routing config. It reads
existing artifacts, creates in-memory QA cases, calls candidate QA providers,
and writes experiment evidence under 04_Work/_experiments plus one report under
07_Reports.
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
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from novel_pipeline.config import load_app_config  # noqa: E402
from novel_pipeline.providers.base import ProviderRunner, classify_provider_response  # noqa: E402
from novel_pipeline.types import ProviderRequest  # noqa: E402


EXPERIMENT_ROOT = PROJECT_ROOT / "04_Work" / "_experiments"
REPORT_ROOT = PROJECT_ROOT / "07_Reports"
OPENROUTER_CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"

OPENROUTER_PRICES = {
    "deepseek/deepseek-v4-pro": {"input_per_m": 0.435, "output_per_m": 0.87},
    "deepseek/deepseek-v4-flash": {"input_per_m": 0.0983, "output_per_m": 0.1966},
}

PASS_BLOCKS = [
    "ch001-block-001",
    "ch003-block-003",
    "ch005-block-001",
    "ch008-block-003",
    "ch011-block-002",
    "ch016-block-001",
    "ch021-block-001",
    "ch023-block-004",
    "ch034-block-002",
    "ch042-block-002",
]

HISTORICAL_BLOCKS = [
    ("ch014-block-005", "historical_omission", "omission"),
    ("ch026-block-004", "historical_glossary_loss", "glossary"),
    ("ch029-block-005", "historical_chinese_leakage", "chinese"),
    ("ch037-block-002", "historical_sentence_drop", "omission"),
    ("ch044-block-001", "historical_hallucination", "addition"),
    ("ch013-block-001", "historical_name_drift", "glossary"),
    ("ch043-block-006", "historical_format_leakage", "chinese"),
    ("ch017-block-003", "historical_unsupported_addition", "addition"),
    ("ch019-block-005", "historical_truncation", "omission"),
    ("ch041-block-002", "historical_meaning_drift", "meaning"),
]

ADVERSARIAL_BLOCKS = [
    ("ch003-block-002", "drop_final_paragraph", "omission"),
    ("ch005-block-004", "prepend_fake_news", "addition"),
    ("ch009-block-003", "duncan_name_corrupt", "glossary"),
    ("ch012-block-003", "insert_chinese", "chinese"),
    ("ch018-block-004", "remove_dialogue", "omission"),
    ("ch023-block-002", "unsupported_emotion", "addition"),
    ("ch028-block-004", "wrong_entity", "glossary"),
    ("ch032-block-006", "truncate_half", "omission"),
    ("ch038-block-005", "perspective_drift", "perspective"),
    ("ch045-block-003", "tone_summary", "meaning"),
]


@dataclass(frozen=True)
class Case:
    case_id: str
    group: str
    block_id: str
    expected_pass: bool
    severity: str
    error_type: str
    source_text: str
    literal_text: str
    refined_text: str
    mutation_note: str


@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    provider: str
    model: str
    request_options: dict[str, Any] | None = None
    system_prompt: str = "You are a strict translation QA judge. Return only PASS or FAIL line."


def _now_id() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _safe_write_json(path: Path, data: Any) -> None:
    text = json.dumps(data, ensure_ascii=False, indent=2)
    _assert_no_secret(text, path)
    path.write_text(text + "\n", encoding="utf-8")


def _safe_write_text(path: Path, text: str) -> None:
    _assert_no_secret(text, path)
    path.write_text(text, encoding="utf-8")


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


def _openrouter_key_candidates() -> list[str]:
    values: list[str] = []
    seen: set[str] = set()
    for value in (os.environ.get("NOVEL_OPENROUTER_API", ""), _read_user_env("NOVEL_OPENROUTER_API")):
        stripped = value.strip()
        if stripped and stripped not in seen:
            values.append(stripped)
            seen.add(stripped)
    return values


def _assert_no_secret(text: str, path: Path) -> None:
    for key in _openrouter_key_candidates():
        if key and key in text:
            raise RuntimeError(f"Refusing to write API key to {path}")
    if "Bearer sk-" in text or "sk-or-" in text:
        raise RuntimeError(f"Refusing to write bearer token fragment to {path}")


def _safe_error_preview(value: str) -> str:
    text = value.replace("\r", " ").replace("\n", " ").strip()
    for key in _openrouter_key_candidates():
        if key:
            text = text.replace(key, "<NOVEL_OPENROUTER_API>")
    text = re.sub(r"sk-or-[A-Za-z0-9_-]+", "<NOVEL_OPENROUTER_API>", text)
    return text[:1000]


def _artifact_paths(block_id: str) -> tuple[Path, Path]:
    chapter = block_id.split("-block-")[0]
    return (
        PROJECT_ROOT / "04_Work" / chapter / f"{block_id}.literal.json",
        PROJECT_ROOT / "04_Work" / chapter / f"{block_id}.refined.json",
    )


def _load_block_text(block_id: str) -> tuple[str, str, str]:
    literal_path, refined_path = _artifact_paths(block_id)
    literal = _read_json(literal_path)
    refined = _read_json(refined_path)
    source_text = str(literal.get("source_text") or "\n".join(
        str(item.get("source_sentence", "")) for item in literal.get("sentence_pairs", [])
    ))
    literal_text = "\n\n".join(
        str(item.get("literal_sentence", "")) for item in literal.get("sentence_pairs", [])
    )
    refined_text = str(refined.get("refined_text") or refined.get("text") or "")
    return source_text, literal_text, refined_text


def _paragraphs(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"\n\s*\n", text.strip()) if part.strip()]


def _mutate(text: str, kind: str) -> tuple[str, str]:
    paragraphs = _paragraphs(text)
    if not paragraphs:
        return text + "\n\nนี่คือข้อความเพิ่มที่ไม่มีในต้นฉบับ", "added unsupported sentence"
    if kind in {"omission", "historical_omission", "historical_sentence_drop"}:
        if len(paragraphs) > 1:
            return "\n\n".join(paragraphs[:-1]), "removed final paragraph"
        words = text.split()
        return " ".join(words[: max(1, len(words) // 2)]), "truncated second half"
    if kind in {"addition", "historical_hallucination", "historical_unsupported_addition"}:
        return "ในปริสสันของปรานด์ " + text, "prepended unsupported hallucinated phrase"
    if kind in {"glossary", "historical_glossary_loss", "historical_name_drift"}:
        replacements = [
            ("ดันแคน", "ดันแคง"),
            ("อลิซ", "อาลิซ"),
            ("เรือผู้ไร้บ้าน", "เรือสูญถิ่น"),
            ("สุริยเทพที่แท้จริง", "เทพอาทิตย์แท้"),
        ]
        for old, new in replacements:
            if old in text:
                return text.replace(old, new, 1), f"changed glossary/name {old} -> {new}"
        return text.replace(paragraphs[0], paragraphs[0] + " คำเรียกเฉพาะถูกเปลี่ยนผิด"), "added glossary drift"
    if kind in {"chinese", "historical_chinese_leakage", "historical_format_leakage"}:
        return text + "\n\n亚空间", "appended Han Chinese leakage"
    if kind in {"perspective", "perspective_drift"}:
        if "ผม" in text:
            return text.replace("ผม", "เขา", 2), "changed first-person pronoun to third-person"
        return text.replace(paragraphs[0], "เขาคิดว่า " + paragraphs[0], 1), "forced perspective drift"
    if kind in {"meaning", "historical_meaning_drift", "tone_summary"}:
        return paragraphs[0] + "\n\nสรุปแล้วเหตุการณ์ทั้งหมดไม่ได้สำคัญนัก", "replaced detail with unsupported summary"
    if kind == "drop_final_paragraph":
        return "\n\n".join(paragraphs[:-1] or paragraphs), "removed final paragraph"
    if kind == "prepend_fake_news":
        return "หนังสือพิมพ์ยืนยันว่าเรื่องทั้งหมดเป็นข่าวปลอม " + text, "prepended unsupported claim"
    if kind == "duncan_name_corrupt":
        return text.replace("ดันแคน", "ดันแคง", 1), "corrupted Duncan name"
    if kind == "insert_chinese":
        return text + "\n\n灵界边缘", "inserted Han Chinese"
    if kind == "remove_dialogue":
        without_dialogue = re.sub(r"[“\"].+?[”\"]", "", text, count=1, flags=re.S).strip()
        return without_dialogue or "\n\n".join(paragraphs[1:] or paragraphs), "removed dialogue segment"
    if kind == "unsupported_emotion":
        return text + "\n\nเขารู้สึกดีใจอย่างสุดซึ้งทั้งที่ไม่มีเหตุผลใดรองรับ", "added unsupported emotion"
    if kind == "wrong_entity":
        return text.replace("คริสตจักร", "สมาคมนักผจญภัย", 1), "changed entity"
    if kind == "truncate_half":
        words = text.split()
        return " ".join(words[: max(1, len(words) // 2)]), "truncated half of text"
    return text + "\n\nข้อความนี้ไม่มีในต้นฉบับ", "added unsupported text"


def _build_cases(limit: int | None = None) -> list[Case]:
    cases: list[Case] = []
    for block_id in PASS_BLOCKS:
        source, literal, refined = _load_block_text(block_id)
        _validate_known_pass_fixture(block_id, refined)
        cases.append(Case(
            case_id=f"pass__{block_id}",
            group="known_pass",
            block_id=block_id,
            expected_pass=True,
            severity="none",
            error_type="none",
            source_text=source,
            literal_text=literal,
            refined_text=refined,
            mutation_note="current QA-passed refined artifact",
        ))
    for block_id, mutation, error_type in HISTORICAL_BLOCKS:
        source, literal, refined = _load_block_text(block_id)
        bad, note = _mutate(refined, mutation)
        cases.append(Case(
            case_id=f"historical__{block_id}__{error_type}",
            group="historical_recovery_derived",
            block_id=block_id,
            expected_pass=False,
            severity="severe",
            error_type=error_type,
            source_text=source,
            literal_text=literal,
            refined_text=bad,
            mutation_note=note,
        ))
    for block_id, mutation, error_type in ADVERSARIAL_BLOCKS:
        source, literal, refined = _load_block_text(block_id)
        bad, note = _mutate(refined, mutation)
        cases.append(Case(
            case_id=f"adversarial__{block_id}__{error_type}",
            group="adversarial",
            block_id=block_id,
            expected_pass=False,
            severity="severe",
            error_type=error_type,
            source_text=source,
            literal_text=literal,
            refined_text=bad,
            mutation_note=note,
        ))
    if limit is not None:
        return cases[:limit]
    return cases


def _validate_known_pass_fixture(block_id: str, refined: str) -> None:
    if re.search(r"[\u4e00-\u9fff]", refined):
        raise ValueError(f"Known-pass fixture {block_id} contains Han Chinese in refined text.")
    blocked_terms = ("ดันแคง", "ดันแค้น", "摆")
    for term in blocked_terms:
        if term in refined:
            raise ValueError(f"Known-pass fixture {block_id} contains suspicious term {term!r}.")


def _build_prompt(case: Case) -> str:
    return (
        "You are the QA judge for a Chinese-to-Thai novel translation pipeline.\n"
        "Output exactly one line in this format:\n"
        "PASS: <concise reason>\n"
        "or\n"
        "FAIL: <concise reason>\n\n"
        "Check omissions, additions, meaning drift, glossary/name consistency, Chinese leakage, and tone.\n"
        "A FAIL is required for any missing sentence/paragraph, unsupported addition, wrong name/glossary term, "
        "untranslated Chinese in Thai body text, perspective drift, or summary replacing detail.\n\n"
        f"CASE_ID: {case.case_id}\n"
        f"CHINESE_SOURCE:\n{case.source_text[:3500]}\n\n"
        f"THAI_LITERAL:\n{case.literal_text[:3500]}\n\n"
        f"THAI_REFINED_TO_JUDGE:\n{case.refined_text[:3500]}\n"
    )


def _post_openrouter(
    model: str,
    prompt: str,
    timeout: int,
    request_options: dict[str, Any] | None = None,
    system_prompt: str = "You are a strict translation QA judge. Return only PASS or FAIL line.",
) -> dict[str, Any]:
    keys = _openrouter_key_candidates()
    if not keys:
        return {"ok": False, "error": "missing_openrouter_key", "latency_seconds": 0.0}
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.0,
        "max_tokens": 500,
    }
    if request_options:
        payload.update(request_options)
    body = json.dumps(payload).encode("utf-8")
    last_error = ""
    for index, key in enumerate(keys):
        request = urllib.request.Request(
            OPENROUTER_CHAT_URL,
            data=body,
            method="POST",
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://local.novel-pipeline.invalid",
                "X-OpenRouter-Title": "Novel Pipeline QA Provider Benchmark",
            },
        )
        started = time.perf_counter()
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                raw = response.read().decode("utf-8", errors="replace")
                elapsed = time.perf_counter() - started
                parsed = json.loads(raw)
                content = parsed.get("choices", [{}])[0].get("message", {}).get("content", "")
                return {
                    "ok": True,
                    "status": response.status,
                    "latency_seconds": round(elapsed, 3),
                    "stdout": str(content),
                    "usage": parsed.get("usage", {}),
                    "returned_model": parsed.get("model"),
                    "finish_reason": parsed.get("choices", [{}])[0].get("finish_reason"),
                }
        except urllib.error.HTTPError as exc:
            elapsed = time.perf_counter() - started
            last_error = _safe_error_preview(exc.read().decode("utf-8", errors="replace"))
            if exc.code == 401 and index + 1 < len(keys):
                continue
            return {
                "ok": False,
                "status": exc.code,
                "latency_seconds": round(elapsed, 3),
                "stdout": "",
                "stderr_preview": last_error,
                "error": "http_error",
            }
        except Exception as exc:  # noqa: BLE001
            elapsed = time.perf_counter() - started
            last_error = _safe_error_preview(str(exc))
            return {
                "ok": False,
                "status": None,
                "latency_seconds": round(elapsed, 3),
                "stdout": "",
                "stderr_preview": last_error,
                "error": type(exc).__name__,
            }
    return {"ok": False, "error": "openrouter_error", "stderr_preview": last_error, "latency_seconds": 0.0, "stdout": ""}


def _run_qwen(prompt: str, timeout: int) -> dict[str, Any]:
    config = load_app_config(PROJECT_ROOT / ".system" / "config.yaml")
    runner = ProviderRunner(config.providers["qwen"])
    response = runner.run(
        ProviderRequest(
            prompt=prompt,
            provider="qwen",
            stage="qa",
            model=config.stage_routing["qa_judge"].model or config.providers["qwen"].default_model,
            timeout_seconds=timeout,
        )
    )
    failure_kind = classify_provider_response(response)
    return {
        "ok": not failure_kind,
        "status": response.returncode,
        "latency_seconds": round(float(response.duration_seconds or 0), 3),
        "stdout": response.stdout or "",
        "stderr_preview": _safe_error_preview(response.stderr or ""),
        "error": failure_kind,
        "usage": {},
    }


def _parse_label(stdout: str) -> tuple[str, str]:
    text = (stdout or "").strip()
    if not text:
        return "unknown", ""
    first = text.splitlines()[0].strip()
    upper = first.upper()
    if upper.startswith("PASS"):
        return "pass", first
    if upper.startswith("FAIL"):
        return "fail", first
    lowered = text.lower()
    if '"passed": true' in lowered or "passed: true" in lowered:
        return "pass", first
    if '"passed": false' in lowered or "passed: false" in lowered:
        return "fail", first
    return "unknown", first


def _has_provider_meta(text: str) -> bool:
    return bool(re.search(r"(?i)(as an ai|rate limit|quota|traceback|openrouter shim error|api key|unauthorized)", text or ""))


def _feedback_useful(case: Case, label: str, stdout: str) -> bool:
    if case.expected_pass:
        return label == "pass"
    text = (stdout or "").lower()
    if label != "fail":
        return False
    keyword_sets = {
        "omission": ("omit", "missing", "truncated", "drop", "หาย", "ขาด", "ละ"),
        "addition": ("addition", "added", "unsupported", "extra", "hallucinat", "เพิ่ม", "ไม่มีในต้นฉบับ"),
        "glossary": ("glossary", "name", "term", "wrong", "ชื่อ", "คำศัพท์"),
        "chinese": ("chinese", "han", "untranslated", "จีน", "ยังไม่ได้แปล"),
        "perspective": ("perspective", "viewpoint", "person", "มุมมอง", "บุรุษ"),
        "meaning": ("meaning", "drift", "summary", "detail", "ความหมาย", "สรุป"),
    }
    terms = keyword_sets.get(case.error_type, ())
    return any(term in text for term in terms) or len(text) >= 40


def _estimate_cost(model: str, usage: dict[str, Any]) -> float | None:
    prices = OPENROUTER_PRICES.get(model)
    if not prices:
        return None
    try:
        input_tokens = int(usage.get("prompt_tokens") or usage.get("input_tokens") or 0)
        output_tokens = int(usage.get("completion_tokens") or usage.get("output_tokens") or 0)
    except (TypeError, ValueError):
        return None
    return (input_tokens * prices["input_per_m"] / 1_000_000) + (output_tokens * prices["output_per_m"] / 1_000_000)


def _score_case(case: Case, result: dict[str, Any], model: str) -> dict[str, Any]:
    label, first_line = _parse_label(result.get("stdout", ""))
    expected_label = "pass" if case.expected_pass else "fail"
    provider_ok = bool(result.get("ok"))
    parse_ok = label in {"pass", "fail"}
    label_correct = label == expected_label
    false_negative = (not case.expected_pass) and label == "pass"
    false_positive = case.expected_pass and label == "fail"
    meta_leak = _has_provider_meta(result.get("stdout", "")) or _has_provider_meta(result.get("stderr_preview", ""))
    useful = _feedback_useful(case, label, result.get("stdout", ""))
    severe_false_negative = false_negative and case.severity == "severe"
    score = 0
    if provider_ok:
        score += 15
    if parse_ok:
        score += 10
    if label_correct:
        score += 35
    if useful:
        score += 20
    if not meta_leak:
        score += 10
    if not severe_false_negative:
        score += 10
    return {
        "score": score,
        "label": label,
        "first_line": first_line,
        "expected_label": expected_label,
        "provider_ok": provider_ok,
        "parse_ok": parse_ok,
        "label_correct": label_correct,
        "false_negative": false_negative,
        "false_positive": false_positive,
        "severe_false_negative": severe_false_negative,
        "feedback_useful": useful,
        "provider_meta_leak": meta_leak,
        "estimated_cost_usd": _estimate_cost(model, result.get("usage") or {}),
    }


def _run_candidate(candidate: Candidate, case: Case, timeout: int) -> dict[str, Any]:
    prompt = _build_prompt(case)
    if candidate.provider == "openrouter":
        result = _post_openrouter(candidate.model, prompt, timeout, candidate.request_options, candidate.system_prompt)
    elif candidate.provider == "qwen":
        result = _run_qwen(prompt, timeout)
    else:
        raise ValueError(candidate.provider)
    score = _score_case(case, result, candidate.model)
    return {
        "candidate_id": candidate.candidate_id,
        "provider": candidate.provider,
        "model": candidate.model,
        "request_options": candidate.request_options or {},
        "case": {
            "case_id": case.case_id,
            "group": case.group,
            "block_id": case.block_id,
            "expected_pass": case.expected_pass,
            "severity": case.severity,
            "error_type": case.error_type,
            "mutation_note": case.mutation_note,
        },
        "result": result,
        "score": score,
    }


def _record_path(out_dir: Path, candidate: Candidate, case: Case) -> Path:
    return out_dir / candidate.candidate_id / f"{case.case_id}.json"


def _aggregate(records: list[dict[str, Any]]) -> dict[str, Any]:
    by_candidate: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        by_candidate.setdefault(record["candidate_id"], []).append(record)
    summary: dict[str, Any] = {}
    for candidate_id, rows in by_candidate.items():
        calls = len(rows)
        scores = [row["score"]["score"] for row in rows]
        latencies = [float(row["result"].get("latency_seconds") or 0) for row in rows]
        costs = [row["score"]["estimated_cost_usd"] for row in rows if row["score"]["estimated_cost_usd"] is not None]
        false_negatives = sum(1 for row in rows if row["score"]["false_negative"])
        severe_false_negatives = sum(1 for row in rows if row["score"]["severe_false_negative"])
        false_positives = sum(1 for row in rows if row["score"]["false_positive"])
        parse_failures = sum(1 for row in rows if not row["score"]["parse_ok"])
        provider_failures = sum(1 for row in rows if not row["score"]["provider_ok"])
        summary[candidate_id] = {
            "provider": rows[0]["provider"],
            "model": rows[0]["model"],
            "request_options": rows[0].get("request_options") or {},
            "calls": calls,
            "avg_score": round(sum(scores) / calls, 2) if calls else 0,
            "false_negatives": false_negatives,
            "severe_false_negatives": severe_false_negatives,
            "false_positives": false_positives,
            "parse_failures": parse_failures,
            "provider_failures": provider_failures,
            "avg_latency_seconds": round(sum(latencies) / calls, 3) if calls else 0,
            "total_estimated_cost_usd": round(sum(costs), 8) if costs else None,
            "estimated_cost_per_100_blocks_usd": round((sum(costs) / len(costs)) * 100, 6) if costs else None,
        }
    return summary


def _candidate_manifest(records: list[dict[str, Any]], all_candidates: dict[str, Candidate]) -> list[dict[str, str]]:
    ids: list[str] = []
    seen: set[str] = set()
    for record in records:
        candidate_id = record["candidate_id"]
        if candidate_id not in seen:
            seen.add(candidate_id)
            ids.append(candidate_id)
    return [all_candidates[candidate_id].__dict__ for candidate_id in ids if candidate_id in all_candidates]


def _recommend(summary: dict[str, Any]) -> str:
    pro = summary.get("openrouter_v4_pro")
    flash = summary.get("openrouter_v4_flash")
    flash_reasoning = summary.get("openrouter_v4_flash_reasoning")
    qwen = summary.get("qwen_cli")
    if flash_reasoning:
        if flash_reasoning["severe_false_negatives"] == 0 and flash_reasoning["parse_failures"] == 0:
            if qwen and flash_reasoning["avg_score"] >= qwen["avg_score"] - 5:
                return (
                    "deepseek/deepseek-v4-flash with reasoning enabled is a viable QA primary candidate in this "
                    "fixture set; run one bounded production-probe milestone before changing routing."
                )
            return (
                "deepseek/deepseek-v4-flash with reasoning enabled is safer than the normal Flash candidate, "
                "but it still does not clearly beat the Qwen CLI baseline; keep production QA routing unchanged "
                "until a bounded production probe proves operational stability."
            )
        return (
            "Do not promote deepseek/deepseek-v4-flash with reasoning enabled to QA primary yet. It produced zero "
            "severe false negatives in this fixture set, but its structured-output reliability is not acceptable "
            f"({flash_reasoning['parse_failures']} parse failures); keep production QA routing unchanged for now."
        )
    if not pro or not flash:
        return "Insufficient OpenRouter data; keep current QA routing until the benchmark can be rerun."
    qwen_quality_ok = bool(qwen and qwen["severe_false_negatives"] == 0 and qwen["avg_score"] >= 85)
    qwen_operationally_clean = bool(qwen_quality_ok and qwen["provider_failures"] == 0 and qwen["parse_failures"] == 0)
    if flash["severe_false_negatives"] == 0 and (pro["avg_score"] - flash["avg_score"]) <= 5:
        fallback = "deepseek/deepseek-v4-pro"
        if qwen_operationally_clean:
            fallback = "qwen CLI, then deepseek/deepseek-v4-pro"
        return f"Use deepseek/deepseek-v4-flash as QA primary; fallback to {fallback}. It stayed within the quality gate while reducing cost."
    if pro["severe_false_negatives"] == 0:
        fallback = "deepseek/deepseek-v4-flash"
        if qwen_operationally_clean:
            fallback = "qwen CLI, then deepseek/deepseek-v4-flash"
        return f"Keep deepseek/deepseek-v4-pro as QA primary; fallback to {fallback}. Flash did not clear the severe-false-negative gate."
    if qwen_quality_ok:
        return (
            "Do not promote deepseek/deepseek-v4-flash to QA primary. Qwen CLI was the strongest semantic judge "
            "but is too slow or operationally unstable for primary routing in this run; keep production QA routing "
            "unchanged for now, preserve Qwen as an important fallback/arbiter, and run a follow-up prompt/output-format "
            "stabilization pass before any QA routing change."
        )
    return "No candidate cleared the severe-false-negative gate; keep QA routing unchanged and rerun with repaired providers."


def _report(run_id: str, cases: list[Case], records: list[dict[str, Any]], summary: dict[str, Any]) -> str:
    compared = ", ".join(f"`{candidate_id}`" for candidate_id in summary)
    lines = [
        f"# QA Provider Cost/Quality Benchmark - {run_id}",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "## Scope",
        "",
        "- Non-production QA-only comparison.",
        "- Production routing was not changed.",
        f"- Compared candidates: {compared}.",
        f"- Cases: {len(cases)} total: 10 known-pass, 10 historical-recovery-derived fail cases, 10 adversarial fail cases.",
        "",
        "## Summary",
        "",
        "| Candidate | Provider | Model | Request options | Calls | Avg score | False negatives | Severe false negatives | False positives | Parse failures | Provider failures | Avg latency | Est. cost | Est. cost / 100 blocks |",
        "| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for candidate_id, data in summary.items():
        cost = data["total_estimated_cost_usd"]
        per_100 = data["estimated_cost_per_100_blocks_usd"]
        options = json.dumps(data.get("request_options") or {}, ensure_ascii=False, separators=(",", ":"))
        lines.append(
            f"| `{candidate_id}` | {data['provider']} | `{data['model']}` | `{options}` | {data['calls']} | {data['avg_score']:.2f} | "
            f"{data['false_negatives']} | {data['severe_false_negatives']} | {data['false_positives']} | "
            f"{data['parse_failures']} | {data['provider_failures']} | {data['avg_latency_seconds']:.3f}s | "
            f"{cost if cost is not None else 'n/a'} | {per_100 if per_100 is not None else 'n/a'} |"
        )
    lines.extend(["", "## Recommendation", "", _recommend(summary), "", "## Per-Case Results", ""])
    lines.append("| Candidate | Case | Group | Expected | Predicted | Score | Latency | Cost | First line |")
    lines.append("| --- | --- | --- | --- | --- | ---: | ---: | ---: | --- |")
    for record in records:
        score = record["score"]
        result = record["result"]
        case = record["case"]
        first = str(score["first_line"]).replace("|", "\\|")[:180]
        cost = score["estimated_cost_usd"]
        lines.append(
            f"| `{record['candidate_id']}` | `{case['case_id']}` | {case['group']} | {score['expected_label']} | "
            f"{score['label']} | {score['score']} | {float(result.get('latency_seconds') or 0):.3f}s | "
            f"{cost if cost is not None else 'n/a'} | {first} |"
        )
    lines.extend([
        "",
        "## Fixture Notes",
        "",
        "- Historical-recovery-derived cases use blocks that had historical failed or hard-fail records, then inject one controlled failure when the original bad artifact was not preserved.",
        "- Adversarial cases use current clean artifacts and inject one controlled QA defect.",
        "- The report should be used for QA routing decisions only; it does not evaluate literal translation, refinement, glossary scan, or formatting.",
        "",
        "## Safety",
        "",
        "- No API key or bearer token is written to artifacts or this report.",
        "- No production ledger, glossary notes, source files, chapter work artifacts, final outputs, or provider config are modified by the benchmark.",
    ])
    return "\n".join(lines) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--max-cases", type=int, default=30)
    parser.add_argument("--candidates", default="openrouter_v4_pro,openrouter_v4_flash,openrouter_v4_flash_reasoning,qwen_cli")
    parser.add_argument("--resume-dir", default="")
    parser.add_argument("--case-ids", default="", help="Comma-separated case IDs to run from the fixture set.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    all_candidates = {
        "openrouter_v4_pro": Candidate("openrouter_v4_pro", "openrouter", "deepseek/deepseek-v4-pro"),
        "openrouter_v4_flash": Candidate("openrouter_v4_flash", "openrouter", "deepseek/deepseek-v4-flash"),
        "openrouter_v4_flash_reasoning": Candidate(
            "openrouter_v4_flash_reasoning",
            "openrouter",
            "deepseek/deepseek-v4-flash",
            {"reasoning": {"enabled": True, "exclude": True}},
        ),
        "openrouter_v4_flash_reasoning_strict": Candidate(
            "openrouter_v4_flash_reasoning_strict",
            "openrouter",
            "deepseek/deepseek-v4-flash",
            {"max_tokens": 1500, "reasoning": {"enabled": True, "exclude": True}},
            (
                "You are a strict translation QA judge. Return exactly one line. "
                "The first characters of your response must be exactly PASS: or FAIL:. "
                "Do not output markdown, JSON, headings, analysis, or any text before PASS:/FAIL:. "
                "If uncertain, return FAIL: followed by the concrete issue."
            ),
        ),
        "qwen_cli": Candidate("qwen_cli", "qwen", "deepseek-reasoner"),
    }
    selected_ids = [item.strip() for item in args.candidates.split(",") if item.strip()]
    candidates = [all_candidates[item] for item in selected_ids]
    cases = _build_cases(limit=args.max_cases)
    if args.case_ids:
        wanted = {item.strip() for item in args.case_ids.split(",") if item.strip()}
        cases = [case for case in cases if case.case_id in wanted]
        missing = wanted.difference({case.case_id for case in cases})
        if missing:
            raise SystemExit(f"Unknown case IDs: {', '.join(sorted(missing))}")
    if args.resume_dir:
        out_dir = Path(args.resume_dir).resolve()
        run_id = out_dir.name
        out_dir.mkdir(parents=True, exist_ok=True)
    else:
        run_id = f"qa_provider_benchmark_{_now_id()}"
        out_dir = EXPERIMENT_ROOT / run_id
        out_dir.mkdir(parents=True, exist_ok=False)
    REPORT_ROOT.mkdir(parents=True, exist_ok=True)

    case_manifest = [
        {
            "case_id": case.case_id,
            "group": case.group,
            "block_id": case.block_id,
            "expected_pass": case.expected_pass,
            "severity": case.severity,
            "error_type": case.error_type,
            "mutation_note": case.mutation_note,
        }
        for case in cases
    ]
    if not (out_dir / "case_manifest.json").exists():
        _safe_write_json(out_dir / "case_manifest.json", case_manifest)

    records: list[dict[str, Any]] = []
    for candidate in candidates:
        candidate_dir = out_dir / candidate.candidate_id
        candidate_dir.mkdir(parents=True, exist_ok=True)
        for case in cases:
            record_path = _record_path(out_dir, candidate, case)
            if record_path.exists():
                record = _read_json(record_path)
                records.append(record)
                print(
                    f"{candidate.candidate_id} {case.case_id} reused expected={record['score']['expected_label']} "
                    f"predicted={record['score']['label']} score={record['score']['score']} "
                    f"latency={record['result'].get('latency_seconds')}"
                )
                continue
            record = _run_candidate(candidate, case, args.timeout)
            records.append(record)
            _safe_write_json(record_path, record)
            print(
                f"{candidate.candidate_id} {case.case_id} expected={record['score']['expected_label']} "
                f"predicted={record['score']['label']} score={record['score']['score']} "
                f"latency={record['result'].get('latency_seconds')}"
            )

    # Include records from other candidate directories when resuming a partial
    # experiment so the final summary/report covers every completed candidate.
    seen_paths = {_record_path(out_dir, candidate, case).resolve() for candidate in candidates for case in cases}
    if args.resume_dir:
        for path in sorted(out_dir.glob("*/*.json")):
            if path.resolve() in seen_paths:
                continue
            try:
                record = _read_json(path)
            except Exception:
                continue
            if isinstance(record, dict) and "candidate_id" in record and "score" in record:
                records.append(record)

    summary = _aggregate(records)
    payload = {
        "run_id": run_id,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "candidates": _candidate_manifest(records, all_candidates),
        "cases": case_manifest,
        "summary": summary,
        "records": records,
        "recommendation": _recommend(summary),
    }
    _safe_write_json(out_dir / "benchmark_summary.json", payload)
    report_path = REPORT_ROOT / f"{run_id}.md"
    _safe_write_text(report_path, _report(run_id, cases, records, summary))
    print(f"experiment_dir={out_dir}")
    print(f"report_path={report_path}")
    print(f"cases={len(cases)}")
    print(f"calls={len(records)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
