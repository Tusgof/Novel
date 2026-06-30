"""Run a bounded non-production provider probe on one block fixture.

The probe compares OpenRouter candidates against existing CLI providers without
touching the production ledger, chapter work artifacts, glossary notes, final
outputs, or provider routing config.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from novel_pipeline.config import load_app_config  # noqa: E402
from novel_pipeline.prompts import PromptStore  # noqa: E402
from novel_pipeline.providers.base import ProviderRunner, classify_provider_response  # noqa: E402
from novel_pipeline.stages.helpers import format_glossary_subset  # noqa: E402
from novel_pipeline.stages.glossary import parse_candidate_terms  # noqa: E402
from novel_pipeline.stages.translate import parse_literal_pairs  # noqa: E402
from novel_pipeline.types import (  # noqa: E402
    GlossaryEntry,
    LiteralDraft,
    LiteralSentencePair,
    ProviderRequest,
    ProviderSpec,
    RefinedDraft,
    TextBlock,
)


EXPERIMENT_ROOT = PROJECT_ROOT / "04_Work" / "_experiments"
REPORT_ROOT = PROJECT_ROOT / "07_Reports"
RUN_PREFIX = "openrouter_bounded_block_probe"


@dataclass(frozen=True)
class ProbeRoute:
    role: str
    label: str
    provider: str
    model: str
    source: str


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


def _assert_no_secret(text: str, path: Path) -> None:
    keys = [os.environ.get("NOVEL_OPENROUTER_API", "").strip(), _read_user_env("NOVEL_OPENROUTER_API").strip()]
    for key in keys:
        if key and key in text:
            raise RuntimeError(f"Refusing to write API key to {path}")
    bearer_fragment = "Bearer " + "sk-"
    if bearer_fragment in text:
        raise RuntimeError(f"Refusing to write bearer token fragment to {path}")


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


def _openrouter_spec() -> ProviderSpec:
    return ProviderSpec(
        name="openrouter",
        executable=(sys.executable, str(PROJECT_ROOT / "scripts" / "openrouter_provider_shim.py")),
        prompt_flag="",
        prompt_position="positional",
        prompt_transport="stdin",
        model_flag="-m",
        model_position="before_prompt",
        timeout_seconds=360,
        retry_max_attempts=1,
    )


def _runner_for(label: str, config_path: Path) -> ProviderRunner:
    config = load_app_config(config_path)
    if label == "openrouter":
        return ProviderRunner(_openrouter_spec())
    if label == "gemini":
        return ProviderRunner(config.providers["gemini"])
    if label == "qwen":
        return ProviderRunner(config.providers["qwen"])
    raise KeyError(label)


def _block_fixture(block_id: str) -> TextBlock:
    chapter = block_id.split("-block-")[0]
    literal_path = PROJECT_ROOT / "04_Work" / chapter / f"{block_id}.literal.json"
    if literal_path.exists():
        data = _read_json(literal_path)
        source_text = data.get("source_text") or "\n".join(
            item.get("source_sentence", "") for item in data.get("sentence_pairs", [])
        )
    else:
        source_data = _read_json(PROJECT_ROOT / "03_Raw" / chapter / "source.json")
        source_text = str(source_data.get("raw_text", ""))[:2200]
    return TextBlock(
        block_id=block_id,
        chapter_id=chapter,
        block_index=int(block_id.rsplit("-", 1)[-1]),
        source_text=source_text,
        source_language="zh",
    )


def _literal_draft(block_id: str) -> LiteralDraft:
    chapter = block_id.split("-block-")[0]
    data = _read_json(PROJECT_ROOT / "04_Work" / chapter / f"{block_id}.literal.json")
    pairs = tuple(
        LiteralSentencePair(
            source_sentence=item.get("source_sentence", ""),
            literal_sentence=item.get("literal_sentence", ""),
            metadata=item.get("metadata", {}),
        )
        for item in data.get("sentence_pairs", [])
    )
    return LiteralDraft(
        block_id=block_id,
        chapter_id=chapter,
        sentence_pairs=pairs,
        source_text=data.get("source_text", ""),
        provider=str(data.get("provider", "")),
    )


def _refined_text(block_id: str) -> str:
    chapter = block_id.split("-block-")[0]
    data = _read_json(PROJECT_ROOT / "04_Work" / chapter / f"{block_id}.refined.json")
    return str(data.get("refined_text", ""))


def _load_glossary_subset() -> list[GlossaryEntry]:
    wanted = {
        "失乡号",
        "邓肯",
        "爱丽丝",
        "艾伊",
        "黄铜罗盘",
        "灵体之火",
        "异常物品",
        "普兰德城邦",
        "山羊头",
        "人偶小姐",
    }
    entries: list[GlossaryEntry] = []
    for path in sorted((PROJECT_ROOT / "01_Glossary").glob("*.md")):
        term = path.stem
        if term not in wanted:
            continue
        text = path.read_text(encoding="utf-8-sig")
        meta = _frontmatter(text)
        entries.append(
            GlossaryEntry(
                original_term=str(meta.get("original_term") or term),
                thai_term=str(meta.get("thai_term") or ""),
                category=str(meta.get("category") or ""),
                status=str(meta.get("status") or "approved"),
                file_name=path.name,
            )
        )
    return entries


def _frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    meta: dict[str, str] = {}
    for line in text[3:end].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip().strip('"')
    return meta


def _strip_code_fence(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```[a-zA-Z0-9_-]*\s*", "", stripped)
        stripped = re.sub(r"\s*```$", "", stripped)
    return stripped.strip()


def _contains_han(text: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", text))


def _contains_thai(text: str) -> bool:
    return bool(re.search(r"[\u0e00-\u0e7f]", text))


def _provider_meta(text: str) -> bool:
    return bool(re.search(r"(?i)(rate limit|quota|session limit|as an ai|traceback|unauthorized|permission denied)", text))


def _render_prompts(config_path: Path, block_id: str) -> dict[str, str]:
    config = load_app_config(config_path)
    prompt_store = PromptStore(config.workspace.prompts)
    block = _block_fixture(block_id)
    literal = _literal_draft(block_id)
    glossary = _load_glossary_subset()
    glossary_text = format_glossary_subset(glossary)
    source_for_prompt = " ".join(line.strip() for line in block.source_text.splitlines() if line.strip())
    literal_text = "\n\n".join(pair.literal_sentence for pair in literal.sentence_pairs)
    refined_good = _refined_text("ch025-block-005")
    known_bad_refined = (
        "ระหว่างเขากับนกพิราบมีความเชื่อมโยงบางอย่างอยู่ และเมื่อกระตุ้นเปลวไฟแห่งร่างวิญญาณ "
        "ความเชื่อมโยงนั้นจะชัดเจนขึ้น ถึงขั้นที่เขาควบคุมได้ในระดับหนึ่งว่ามันจะไปปรากฏตรงไหน"
    )
    style = config.style_profile_for_name(config.default_style_profile)
    qa_literal = LiteralDraft(
        block_id=block.block_id,
        chapter_id=block.chapter_id,
        sentence_pairs=literal.sentence_pairs,
        source_text=literal.source_text,
        provider=literal.provider,
    )
    qa_refined = RefinedDraft(
        block_id=block.block_id,
        chapter_id=block.chapter_id,
        refined_text=known_bad_refined,
        provider="fixture",
        style_profile=config.default_style_profile,
        source_text=block.source_text,
    )
    return {
        "glossary": prompt_store.render("term_extraction", source_block=block.source_text[:2500]),
        "literal": prompt_store.render(
            "literal_translation",
            source_block=source_for_prompt,
            glossary_subset=glossary_text,
            source_language=block.source_language,
            research_context=config.research_context_text(),
        ),
        "refine": prompt_store.render(
            "refinement",
            literal_draft=literal_text,
            source_block=block.source_text,
            glossary_subset=glossary_text,
            style_instructions=style.instruction_text(),
            retry_feedback="none",
            research_context=config.research_context_text(),
        ),
        "qa": prompt_store.render(
            "qa_judge",
            source_block=block.source_text,
            literal_draft=qa_literal.to_dict(),
            refined_draft=qa_refined.to_dict(),
            glossary_subset=[entry.to_dict() for entry in glossary],
            style_instructions=style.instruction_text(),
            research_context=config.research_context_text(),
        ),
        "format": prompt_store.render("formatting.md", text=refined_good),
    }


def _routes() -> list[ProbeRoute]:
    return [
        ProbeRoute("glossary", "openrouter_gemini3_flash", "openrouter", "google/gemini-3-flash-preview", "openrouter"),
        ProbeRoute("glossary", "current_gemini_pro", "gemini", "pro", "current"),
        ProbeRoute("literal", "openrouter_gemini3_flash", "openrouter", "google/gemini-3-flash-preview", "openrouter"),
        ProbeRoute("literal", "openrouter_deepseek_v4_flash", "openrouter", "deepseek/deepseek-v4-flash", "openrouter"),
        ProbeRoute("literal", "current_gemini_pro", "gemini", "pro", "current"),
        ProbeRoute("refine", "openrouter_gemini3_flash", "openrouter", "google/gemini-3-flash-preview", "openrouter"),
        ProbeRoute("refine", "openrouter_deepseek_v4_flash", "openrouter", "deepseek/deepseek-v4-flash", "openrouter"),
        ProbeRoute("refine", "openrouter_claude_sonnet_4_6", "openrouter", "anthropic/claude-sonnet-4.6", "openrouter"),
        ProbeRoute("qa", "current_qwen_deepseek_reasoner", "qwen", "deepseek-reasoner", "current"),
        ProbeRoute("qa", "openrouter_gemini3_flash", "openrouter", "google/gemini-3-flash-preview", "openrouter"),
        ProbeRoute("qa", "openrouter_deepseek_v4_pro", "openrouter", "deepseek/deepseek-v4-pro", "openrouter"),
        ProbeRoute("format", "openrouter_gemini3_flash", "openrouter", "google/gemini-3-flash-preview", "openrouter"),
        ProbeRoute("format", "openrouter_deepseek_v4_flash", "openrouter", "deepseek/deepseek-v4-flash", "openrouter"),
    ]


def _score(
    role: str,
    stdout: str,
    returncode: int,
    failure_kind: str,
    prompt: str,
    *,
    source_text: str = "",
) -> dict[str, Any]:
    text = _strip_code_fence(stdout)
    checks = {
        "provider_ok": returncode == 0 and not failure_kind,
        "nonempty": bool(text.strip()),
        "no_provider_meta": not _provider_meta(text),
        "thai_when_expected": True,
        "no_han_when_expected": True,
        "json_when_expected": True,
        "production_parseable": True,
        "qa_known_bad_caught": True,
        "format_preserved_length": True,
    }
    if role in {"literal", "refine", "format"}:
        checks["thai_when_expected"] = _contains_thai(text)
        checks["no_han_when_expected"] = not _contains_han(text)
    if role == "glossary":
        checks["production_parseable"] = bool(parse_candidate_terms(text))
    if role == "literal":
        checks["production_parseable"] = bool(parse_literal_pairs(source_text, text))
    if role == "qa":
        lowered = text.lower()
        checks["qa_known_bad_caught"] = (
            "fail" in lowered
            or "passed\": false" in lowered
            or "passed: false" in lowered
            or "omission" in lowered
            or "drift" in lowered
            or "ไม่ผ่าน" in lowered
        )
    if role == "format":
        source_text = prompt.split("TEXT:", 1)[-1].strip() if "TEXT:" in prompt else ""
        if source_text:
            checks["format_preserved_length"] = len(text) >= int(len(source_text) * 0.9)
    score = 0
    weights = {
        "provider_ok": 20,
        "nonempty": 10,
        "no_provider_meta": 10,
        "thai_when_expected": 15,
        "no_han_when_expected": 15,
        "json_when_expected": 0,
        "production_parseable": 10,
        "qa_known_bad_caught": 15,
        "format_preserved_length": 5,
    }
    for key, weight in weights.items():
        if checks[key]:
            score += weight
    hard_fail = not all(checks.values())
    return {"score": score, "hard_fail": hard_fail, "checks": checks}


def _run_route(route: ProbeRoute, prompt: str, config_path: Path, timeout: int) -> dict[str, Any]:
    runner = _runner_for(route.provider, config_path)
    response = runner.run(
        ProviderRequest(
            prompt=prompt,
            provider=runner.spec.name,
            stage=route.role,
            model=route.model,
            timeout_seconds=timeout,
        )
    )
    failure_kind = classify_provider_response(response)
    block = _block_fixture("ch025-block-002")
    score = _score(route.role, response.stdout, response.returncode, failure_kind, prompt, source_text=block.source_text)
    return {
        "role": route.role,
        "label": route.label,
        "provider": route.provider,
        "model": route.model,
        "source": route.source,
        "returncode": response.returncode,
        "duration_seconds": response.duration_seconds,
        "failure_kind": failure_kind,
        "stdout": response.stdout,
        "stderr_preview": (response.stderr or "")[:1000],
        "score": score,
    }


def _summarize(results: list[dict[str, Any]], run_id: str) -> str:
    lines = [
        f"# OpenRouter Bounded Block Probe - {run_id}",
        "",
        "## Summary",
        "",
        "| Role | Route | Provider | Model | Score | Hard fail | Duration | Failure |",
        "| --- | --- | --- | --- | ---: | --- | ---: | --- |",
    ]
    for item in results:
        lines.append(
            f"| {item['role']} | {item['label']} | {item['provider']} | `{item['model']}` | "
            f"{item['score']['score']} | {item['score']['hard_fail']} | "
            f"{float(item.get('duration_seconds') or 0):.2f}s | {item.get('failure_kind') or 'none'} |"
        )
    lines.extend(["", "## Recommendations", ""])
    lines.extend(_recommendations(results))
    lines.extend(
        [
            "",
            "## Scope And Safety",
            "",
            "- Non-production probe only.",
            "- No production ledger, glossary notes, chapter work artifacts, final outputs, or provider routing config were modified by this probe.",
            "- OpenRouter key was read by the shim from process/User environment and never written to artifacts.",
            "- `.system/providers.yaml` changes are proposed only after this report; they are not applied by this script.",
        ]
    )
    return "\n".join(lines) + "\n"


def _best_by_role(results: list[dict[str, Any]], role: str) -> list[dict[str, Any]]:
    rows = [item for item in results if item["role"] == role]
    return sorted(rows, key=lambda item: (item["score"]["hard_fail"], -item["score"]["score"], item["duration_seconds"]))


def _recommendations(results: list[dict[str, Any]]) -> list[str]:
    lines: list[str] = []
    for role in ("glossary", "literal", "refine", "qa", "format"):
        ordered = _best_by_role(results, role)
        if not ordered:
            continue
        winner = ordered[0]
        lines.append(f"- `{role}`: first candidate `{winner['label']}` (`{winner['model']}`), score {winner['score']['score']}, hard_fail={winner['score']['hard_fail']}.")
    lines.extend(
        [
            "",
            "Proposed next routing direction, pending Codex review:",
            "",
            "```yaml",
            "term_extraction: openrouter google/gemini-3-flash-preview",
            "literal_translation: openrouter google/gemini-3-flash-preview",
            "refinement: openrouter google/gemini-3-flash-preview",
            "refinement fallback: openrouter deepseek/deepseek-v4-flash",
            "qa_judge: keep current qwen/deepseek-reasoner unless OpenRouter QA wins the bounded probe",
            "formatting: openrouter google/gemini-3-flash-preview with deterministic validation/local fallback",
            "```",
        ]
    )
    return lines


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=".system/config.yaml")
    parser.add_argument("--block-id", default="ch025-block-002")
    parser.add_argument("--timeout", type=int, default=420)
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    config_path = (PROJECT_ROOT / args.config).resolve()
    run_id = f"{RUN_PREFIX}_{_now_id()}"
    out_dir = EXPERIMENT_ROOT / run_id
    out_dir.mkdir(parents=True, exist_ok=False)
    REPORT_ROOT.mkdir(parents=True, exist_ok=True)

    prompts = _render_prompts(config_path, args.block_id)
    _safe_write_json(out_dir / "prompt_metadata.json", {key: len(value) for key, value in prompts.items()})

    results: list[dict[str, Any]] = []
    for route in _routes():
        prompt = prompts[route.role]
        result = _run_route(route, prompt, config_path, args.timeout)
        results.append(result)
        route_path = out_dir / f"{route.role}__{route.label}.json"
        _safe_write_json(route_path, result)

    summary = {
        "run_id": run_id,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "block_id": args.block_id,
        "results": results,
    }
    _safe_write_json(out_dir / "probe_summary.json", summary)
    report_path = REPORT_ROOT / f"{run_id}.md"
    _safe_write_text(report_path, _summarize(results, run_id))
    print(f"experiment_dir={out_dir}")
    print(f"report_path={report_path}")
    print(f"routes={len(results)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
