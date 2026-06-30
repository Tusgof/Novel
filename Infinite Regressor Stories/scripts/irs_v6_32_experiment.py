from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import unicodedata
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import sys

PIPELINE_ROOT = Path(__file__).resolve().parents[2] / "Deep Sea Embers"
if str(PIPELINE_ROOT) not in sys.path:
    sys.path.insert(0, str(PIPELINE_ROOT))

from novel_pipeline.config import load_app_config  # noqa: E402
from novel_pipeline.text_utils import split_blocks  # noqa: E402


RUN_IDS = (
    "irs-ch001-ch005-v2",
    "irs-ch006-ch010-v1",
    "irs-ch011-ch015-v1",
    "irs-ch016-ch020-v1",
)

SEED_STAGES = ("fetched", "glossary_scanned", "glossary_approved")


@dataclass
class ChapterRisk:
    chapter_id: str
    title: str
    source_chars: int
    source_words: int
    block_count: int
    max_block_words: int
    has_zalgo: bool
    has_long_repeat: bool
    has_footnotes: bool
    has_bracket_messages: bool
    has_system_terms: bool
    has_title_sidecar: bool
    risk_score: int
    risk_reasons: list[str]


def chapter_num(chapter_id: str) -> int:
    return int(chapter_id.removeprefix("ch"))


def chapter_id(num: int) -> str:
    return f"ch{num:03d}"


def parse_range(raw: str) -> list[str]:
    start_raw, end_raw = raw.split("-", 1)
    start = int(start_raw.removeprefix("ch"))
    end = int(end_raw.removeprefix("ch"))
    return [chapter_id(num) for num in range(start, end + 1)]


def parse_chapters(raw: str) -> list[str]:
    chapters: list[str] = []
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            chapters.extend(parse_range(part))
        else:
            chapters.append(part)
    return sorted(dict.fromkeys(chapters), key=chapter_num)


def stable_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_source(novel_dir: Path, cid: str) -> tuple[str, str]:
    path = novel_dir / "03_Raw" / cid / "source.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    title = str(data.get("title") or data.get("chapter_title") or cid)
    text = str(data.get("body") or data.get("text") or data.get("content") or data.get("raw_text") or "")
    return title, text


def source_exists(novel_dir: Path, cid: str) -> bool:
    return (novel_dir / "03_Raw" / cid / "source.json").exists()


def has_zalgo(text: str) -> bool:
    combining = sum(1 for char in text if unicodedata.category(char).startswith("M"))
    return combining >= 8


def has_long_repeat(text: str) -> bool:
    return bool(re.search(r"(.)\1{20,}", text))


def analyze_chapter(novel_dir: Path, config: Any, cid: str) -> ChapterRisk:
    title, text = load_source(novel_dir, cid)
    blocks = split_blocks(
        cid,
        text,
        config.source_language,
        zh_limit=config.chunking.chinese_character_limit,
        non_zh_limit=config.chunking.non_chinese_word_limit,
    )
    block_words = [len((block.source_text or block.text).split()) for block in blocks]
    bracket_messages = bool(re.search(r"\[[^\]]{8,}\]", text))
    system_terms = any(term in text for term in ("Constellation", "Awakener", "Gate", "regressor", "Regression"))
    footnotes = "Footnotes:" in text or bool(re.search(r"\[\d+\]", text))
    zalgo = has_zalgo(text)
    long_repeat = has_long_repeat(text)
    has_sidecar = (novel_dir / "04_Work" / cid / "title.json").exists()

    reasons: list[str] = []
    score = 0
    if zalgo:
        score += 4
        reasons.append("zalgo_or_distorted_sound")
    if long_repeat:
        score += 4
        reasons.append("long_repeated_characters")
    if max(block_words or [0]) >= 1200:
        score += 3
        reasons.append("large_block")
    if len(blocks) >= 3:
        score += 2
        reasons.append("many_blocks")
    if footnotes:
        score += 2
        reasons.append("footnotes")
    if bracket_messages:
        score += 2
        reasons.append("bracket_messages")
    if system_terms:
        score += 1
        reasons.append("system_or_lore_terms")
    if not has_sidecar and re.search(r"[A-Za-z]", title):
        score += 1
        reasons.append("english_title_sidecar_missing")

    return ChapterRisk(
        chapter_id=cid,
        title=title,
        source_chars=len(text),
        source_words=len(text.split()),
        block_count=len(blocks),
        max_block_words=max(block_words or [0]),
        has_zalgo=zalgo,
        has_long_repeat=long_repeat,
        has_footnotes=footnotes,
        has_bracket_messages=bracket_messages,
        has_system_terms=system_terms,
        has_title_sidecar=has_sidecar,
        risk_score=score,
        risk_reasons=reasons,
    )


def latest_stage_status(records: list[dict[str, Any]]) -> dict[str, str]:
    status: dict[str, str] = {}
    for record in records:
        block_id = str(record.get("block_id") or "")
        stage = str(record.get("stage") or "")
        rec_status = str(record.get("status") or "")
        if block_id and stage:
            status[f"{block_id}:{stage}"] = rec_status
    return status


def collect_ledger_metrics(novel_dir: Path) -> dict[str, Any]:
    ledger_path = novel_dir / "06_Logs" / "run_ledger.jsonl"
    if not ledger_path.exists():
        return {
            "records": 0,
            "by_run": {},
            "by_stage_status": {},
            "provider_failures": {},
            "historical_failed_blocks": [],
            "current_failed_qa_blocks": [],
        }
    records: list[dict[str, Any]] = []
    for line in ledger_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if record.get("run_id") in RUN_IDS:
            records.append(record)

    by_run: dict[str, Counter[str]] = defaultdict(Counter)
    by_stage_status: Counter[str] = Counter()
    provider_failures: Counter[str] = Counter()
    historical_failed_blocks: set[str] = set()
    for record in records:
        run_id = str(record.get("run_id"))
        stage = str(record.get("stage"))
        status = str(record.get("status"))
        provider = str(record.get("provider"))
        by_run[run_id][f"{stage}:{status}"] += 1
        by_stage_status[f"{stage}:{status}"] += 1
        if status == "failed":
            historical_failed_blocks.add(str(record.get("block_id")))
            provider_failures[f"{provider}:{stage}"] += 1

    latest = latest_stage_status(records)
    current_failed = sorted(
        key.split(":", 1)[0]
        for key, status in latest.items()
        if key.endswith(":qa") and status == "failed"
    )
    return {
        "records": len(records),
        "by_run": {run: dict(counter) for run, counter in by_run.items()},
        "by_stage_status": dict(by_stage_status),
        "provider_failures": dict(provider_failures),
        "historical_failed_blocks": sorted(historical_failed_blocks),
        "current_failed_qa_blocks": current_failed,
    }


def select_samples(risks: list[ChapterRisk], *, in_sample_pool: list[str], out_sample_pool: list[str], seed: int) -> dict[str, list[str]]:
    risk_by_id = {risk.chapter_id: risk for risk in risks}
    in_ranked = sorted(
        (risk_by_id[cid] for cid in in_sample_pool if cid in risk_by_id),
        key=lambda item: (-item.risk_score, chapter_num(item.chapter_id)),
    )
    in_sample = [risk.chapter_id for risk in in_ranked[:10]]
    rng = random.Random(seed)
    out_candidates = [cid for cid in out_sample_pool if cid in risk_by_id]
    out_sample = sorted(rng.sample(out_candidates, k=min(10, len(out_candidates))), key=chapter_num)
    return {"in_sample": in_sample, "out_of_sample": out_sample}


def write_report(novel_dir: Path, payload: dict[str, Any]) -> tuple[Path, Path]:
    reports_dir = novel_dir / "07_Reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    json_path = reports_dir / f"v6_32_irs_experiment_baseline_{stamp}.json"
    md_path = reports_dir / f"v6_32_irs_experiment_baseline_{stamp}.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# V6.32 IRS Experiment Baseline",
        "",
        f"- Created: {payload['created_at']}",
        f"- Seed: {payload['seed']}",
        f"- In-sample: {', '.join(payload['samples']['in_sample'])}",
        f"- Out-of-sample: {', '.join(payload['samples']['out_of_sample'])}",
        "",
        "## Baseline Ledger Metrics",
        "",
        f"- Records: {payload['ledger_metrics']['records']}",
        f"- Current failed QA blocks: {', '.join(payload['ledger_metrics']['current_failed_qa_blocks']) or 'none'}",
        f"- Historical failed blocks: {len(payload['ledger_metrics']['historical_failed_blocks'])}",
        f"- Provider failures: {payload['ledger_metrics']['provider_failures']}",
        "",
        "## Sample Risk Table",
        "",
        "| chapter | risk | blocks | max words | reasons | title |",
        "| --- | ---: | ---: | ---: | --- | --- |",
    ]
    risks = {risk["chapter_id"]: risk for risk in payload["chapter_risks"]}
    for cid in payload["samples"]["in_sample"] + payload["samples"]["out_of_sample"]:
        risk = risks[cid]
        lines.append(
            f"| {cid} | {risk['risk_score']} | {risk['block_count']} | {risk['max_block_words']} | "
            f"{', '.join(risk['risk_reasons']) or '-'} | {risk['title']} |"
        )
    lines.extend(
        [
            "",
            "## Gate",
            "",
            "- This report is read-only and does not call providers.",
            "- Production scaling remains blocked until in-sample and out-of-sample experiment gates pass.",
        ]
    )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, md_path


def existing_seed_keys(ledger_path: Path, run_id: str) -> set[tuple[str, str]]:
    if not ledger_path.exists():
        return set()
    keys: set[tuple[str, str]] = set()
    for line in ledger_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if record.get("run_id") == run_id:
            keys.add((str(record.get("block_id")), str(record.get("stage"))))
    return keys


def seed_ledger(novel_dir: Path, run_id: str, chapters: list[str], decision_report: str) -> int:
    ledger_dir = novel_dir / "06_Logs"
    ledger_dir.mkdir(parents=True, exist_ok=True)
    ledger_path = ledger_dir / "run_ledger.jsonl"
    existing = existing_seed_keys(ledger_path, run_id)
    now = datetime.now(timezone.utc).isoformat()
    records: list[dict[str, Any]] = []
    for cid in chapters:
        title, text = load_source(novel_dir, cid)
        source_hash = stable_hash(f"{cid}\n{title}\n{text}")
        for stage in SEED_STAGES:
            key = (cid, stage)
            if key in existing:
                continue
            records.append(
                {
                    "run_id": run_id,
                    "block_id": cid,
                    "stage": stage,
                    "status": "completed",
                    "provider": "local",
                    "created_at": now,
                    "input_hash": source_hash,
                    "output_hash": stable_hash(f"{run_id}:{cid}:{stage}:v6.32-seed"),
                    "metadata": {
                        "experiment": "V6.32",
                        "seeded": True,
                        "seed_reason": "non-contiguous isolated experiment sample",
                        "decision_report": decision_report,
                        "chapter_title": title,
                    },
                }
            )
    if records:
        with ledger_path.open("a", encoding="utf-8") as handle:
            for record in records:
                handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    print(f"ledger={ledger_path}")
    print(f"run_id={run_id}")
    print(f"chapters={','.join(chapters)}")
    print(f"records_appended={len(records)}")
    return len(records)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", nargs="?", default="baseline", choices=("baseline", "seed-ledger"))
    parser.add_argument("--novel-dir", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--config", default=".system/config.yaml")
    parser.add_argument("--in-sample-pool", default="ch001-ch020")
    parser.add_argument("--out-sample-pool", default="ch021-ch060")
    parser.add_argument("--seed", type=int, default=632)
    parser.add_argument("--run-id", default="")
    parser.add_argument("--chapters", default="")
    parser.add_argument("--decision-report", default="")
    args = parser.parse_args()

    novel_dir = Path(args.novel_dir).resolve()
    if args.command == "seed-ledger":
        if not args.run_id:
            parser.error("--run-id is required for seed-ledger")
        if not args.chapters:
            parser.error("--chapters is required for seed-ledger")
        seed_ledger(
            novel_dir=novel_dir,
            run_id=args.run_id,
            chapters=parse_chapters(args.chapters),
            decision_report=args.decision_report,
        )
        return 0

    config = load_app_config(novel_dir / args.config)
    in_sample_pool = parse_chapters(args.in_sample_pool)
    out_sample_pool = parse_chapters(args.out_sample_pool)
    chapter_ids = sorted(
        {
            cid
            for cid in in_sample_pool + out_sample_pool
            if source_exists(novel_dir, cid)
        },
        key=chapter_num,
    )
    risks = [analyze_chapter(novel_dir, config, cid) for cid in chapter_ids]
    samples = select_samples(
        risks,
        in_sample_pool=in_sample_pool,
        out_sample_pool=out_sample_pool,
        seed=args.seed,
    )
    payload = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "novel_dir": str(novel_dir),
        "seed": args.seed,
        "in_sample_pool": args.in_sample_pool,
        "out_sample_pool": args.out_sample_pool,
        "samples": samples,
        "chapter_risks": [asdict(risk) for risk in risks],
        "ledger_metrics": collect_ledger_metrics(novel_dir),
    }
    json_path, md_path = write_report(novel_dir, payload)
    print(f"json_report={json_path}")
    print(f"markdown_report={md_path}")
    print(f"in_sample={','.join(samples['in_sample'])}")
    print(f"out_of_sample={','.join(samples['out_of_sample'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
