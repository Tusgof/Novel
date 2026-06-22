from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


SCRIPT_PATH = Path(__file__).resolve()
DSE_ROOT = SCRIPT_PATH.parents[1]
WORKSPACE_ROOT = DSE_ROOT.parent
REGISTRY_PATH = WORKSPACE_ROOT / "00_Config" / "novel_registry.json"
MOONREAD_ROOT = WORKSPACE_ROOT / "MoonRead"
REPORT_ROOT = WORKSPACE_ROOT / "07_Reports"
KNOWN_GLOSSARY_NEAR_MISSES = {
    "Kaelen": ["ไคลน์", "ไคล์น"],
    "Kaelen Jacobs": ["ไคลน์", "ไคล์น"],
    "Twisted Man": ["ทวิสเต็ดแมน"],
    "The Anomaly": ["อโนมาลี"],
    "Anomaly": ["อโนมาลี"],
}


@dataclass
class Finding:
    severity: str
    category: str
    path: str
    message: str
    evidence: str = ""


@dataclass
class GlossaryTerm:
    original: str
    thai: str
    category: str
    path: Path


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def load_registry() -> dict:
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def filter_registry(registry: dict, novel_filter: str | None) -> dict:
    if not novel_filter:
        return registry
    requested = {part.strip().lower() for part in novel_filter.split(",") if part.strip()}
    novels = [
        novel
        for novel in registry.get("novels", [])
        if str(novel.get("slug", "")).lower() in requested
        or str(novel.get("folder", "")).lower() in requested
    ]
    if not novels:
        available = ", ".join(str(novel.get("slug", "")) for novel in registry.get("novels", []))
        raise SystemExit(f"Unknown --novel value: {novel_filter}. Available: {available}")
    filtered = dict(registry)
    filtered["novels"] = novels
    return filtered


def registry_path_markers(registry: dict) -> list[str]:
    markers: list[str] = []
    for novel in registry.get("novels", []):
        folder = str(novel.get("folder", "")).replace("/", "\\")
        slug = str(novel.get("slug", ""))
        if folder:
            markers.append(f"\\{folder}\\")
        if slug:
            markers.append(f"\\books\\{slug}\\")
    return markers


def filter_findings_by_registry(findings: list[Finding], registry: dict) -> list[Finding]:
    markers = registry_path_markers(registry)
    if not markers:
        return findings
    filtered: list[Finding] = []
    for finding in findings:
        normalized_path = finding.path.replace("/", "\\")
        if any(marker in normalized_path for marker in markers):
            filtered.append(finding)
    return filtered


def normalize_chapter(value: str) -> str:
    value = value.strip()
    if value.startswith("ch"):
        return value
    if value.isdigit():
        return f"ch{int(value):03d}"
    return value


def parse_chapter_scope(raw: str | None) -> set[str] | None:
    if not raw:
        return None
    chapters: set[str] = set()
    for token in raw.split(","):
        token = token.strip()
        if not token:
            continue
        if "-" in token:
            start_raw, end_raw = token.split("-", 1)
            start = normalize_chapter(start_raw)
            end = normalize_chapter(end_raw)
            if start.startswith("ch") and end.startswith("ch") and start[2:].isdigit() and end[2:].isdigit():
                for number in range(int(start[2:]), int(end[2:]) + 1):
                    chapters.add(f"ch{number:03d}")
                continue
        chapters.add(normalize_chapter(token))
    return chapters


def in_scope(chapter: str, scoped: set[str] | None) -> bool:
    return scoped is None or chapter in scoped


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = read_text(path).lstrip("\ufeff")
    match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return {}
    values: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip("'\"")
    return values


def parse_inline_list(raw: str) -> list[str]:
    raw = raw.strip()
    if not raw.startswith("[") or not raw.endswith("]"):
        return []
    return [part.strip().strip("'\"") for part in raw[1:-1].split(",") if part.strip()]


def iter_markdown_files(root: Path, scoped: set[str] | None) -> Iterable[Path]:
    if not root.exists():
        return []
    nested = sorted(root.glob("ch*/ch*.md"))
    paths = nested if nested else sorted(root.glob("ch*.md"))
    return [path for path in paths if in_scope(path.parent.name if path.parent.name.startswith("ch") else path.stem, scoped)]


def load_guardrail_module():
    path = DSE_ROOT / "scripts" / "check_output_quality_guardrails.py"
    spec = importlib.util.spec_from_file_location("sentinel_guardrails", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load guardrail module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["sentinel_guardrails"] = module
    spec.loader.exec_module(module)
    return module


def collect_existing_guardrails(scoped: set[str] | None) -> list[Finding]:
    module = load_guardrail_module()
    issues: list[str] = []
    module.check_registry_title_policies(issues)
    module.check_hgd_required_source_beats(issues)
    module.check_hgd_pronoun_policy(issues)
    module.check_registry_truncation_against_source(issues)

    module.check_paragraph_density(module.DSE / "05_Output", issues, scoped_chapters=scoped)
    module.check_duplicate_title_paragraphs(module.DSE / "05_Output", issues, scoped_chapters=scoped)
    module.check_translation_metadata_leakage(module.DSE / "05_Output", issues, scoped_chapters=scoped)
    module.check_duplicate_title_paragraphs(
        module.MOONREAD / "content/generated/books/deep-sea-embers/chapters",
        issues,
        scoped_chapters=scoped,
    )
    module.check_translation_metadata_leakage(
        module.MOONREAD / "content/generated/books/deep-sea-embers/chapters",
        issues,
        scoped_chapters=scoped,
    )
    module.check_paragraph_density(
        module.HGD / "05_Output",
        issues,
        max_chars=module.MAX_HGD_PARAGRAPH_CHARS,
        scoped_chapters=scoped,
    )
    module.check_malformed_markdown_artifacts(module.HGD / "05_Output", issues, scoped_chapters=scoped)
    module.check_translation_metadata_leakage(module.HGD / "05_Output", issues, scoped_chapters=scoped)
    module.check_hgd_approved_glossary_leakage(module.HGD / "05_Output", issues, scoped_chapters=scoped)
    module.check_malformed_markdown_artifacts(
        module.MOONREAD / "content/generated/books/horror-game-developer/chapters",
        issues,
        scoped_chapters=scoped,
    )
    module.check_translation_metadata_leakage(
        module.MOONREAD / "content/generated/books/horror-game-developer/chapters",
        issues,
        scoped_chapters=scoped,
    )
    module.check_hgd_approved_glossary_leakage(
        module.MOONREAD / "content/generated/books/horror-game-developer/chapters",
        issues,
        scoped_chapters=scoped,
    )

    return [
        Finding("blocker", "existing_guardrail", issue.split(":", 1)[0], issue)
        for issue in issues
    ]


def approved_glossary_terms(novel_root: Path, findings: list[Finding]) -> list[GlossaryTerm]:
    glossary_root = novel_root / "01_Glossary"
    terms: list[GlossaryTerm] = []
    if not glossary_root.exists():
        return terms
    for path in sorted(glossary_root.glob("*.md")):
        meta = parse_frontmatter(path)
        if meta.get("status") != "approved":
            continue
        thai = meta.get("thai_term", "").strip()
        if not thai or "?" in thai or "\ufffd" in thai:
            findings.append(
                Finding(
                    "blocker",
                    "glossary_health",
                    str(path),
                    "approved glossary term has unusable thai_term",
                    thai,
                )
            )
            continue
        category = meta.get("category", "").strip().lower()
        originals = [meta.get("original_term", "").strip(), *parse_inline_list(meta.get("aliases", ""))]
        for original in originals:
            if original and original != thai and re.search(r"[A-Za-z]", original) and original not in thai:
                terms.append(GlossaryTerm(original=original, thai=thai, category=category, path=path))
    terms.sort(key=lambda item: len(item.original), reverse=True)
    return terms


def source_contains_term(text: str, original: str) -> bool:
    if original not in text:
        return False
    if re.search(r"[A-Za-z]", original):
        return bool(re.search(rf"(?<![A-Za-z]){re.escape(original)}(?![A-Za-z])", text))
    return original in text


def glossary_coverage_severity(category: str) -> str:
    if category in {"character", "entity", "title", "system", "skill", "rank"}:
        return "blocker"
    if category in {"organization", "location", "item", "technique", "event"}:
        return "major"
    return "minor"


def chapter_from_markdown_path(path: Path) -> str:
    if path.parent.name.startswith("ch"):
        return path.parent.name
    return path.stem


def source_text_for_chapter(novel_root: Path, raw_dir: str, chapter: str) -> str:
    source_path = novel_root / raw_dir / chapter / "source.json"
    if not source_path.exists():
        return ""
    try:
        data = json.loads(read_text(source_path))
    except (OSError, json.JSONDecodeError):
        return ""
    parts: list[str] = []
    for key in ("title", "raw_title", "raw_text", "source_text", "text"):
        value = data.get(key)
        if isinstance(value, str):
            parts.append(value)
    blocks = data.get("blocks")
    if isinstance(blocks, list):
        for block in blocks:
            if not isinstance(block, dict):
                continue
            for key in ("source_text", "raw_text", "text"):
                value = block.get(key)
                if isinstance(value, str):
                    parts.append(value)
    return "\n".join(parts)


def final_output_path_for_chapter(novel_root: Path, output_dir: str, chapter: str) -> Path:
    return novel_root / output_dir / chapter / f"{chapter}.md"


def reader_output_path_for_chapter(slug: str, chapter: str) -> Path:
    return MOONREAD_ROOT / "content/generated/books" / slug / "chapters" / f"{chapter}.md"


def chapters_with_outputs(novel_root: Path, output_dir: str, slug: str, scoped: set[str] | None) -> set[str]:
    chapters: set[str] = set()
    for root in [
        novel_root / output_dir,
        MOONREAD_ROOT / "content/generated/books" / slug / "chapters",
    ]:
        for path in iter_markdown_files(root, scoped):
            chapters.add(chapter_from_markdown_path(path))
    return chapters


def format_near_miss_evidence(term: GlossaryTerm, text: str) -> str:
    misses = [variant for variant in KNOWN_GLOSSARY_NEAR_MISSES.get(term.original, []) if variant in text]
    if misses:
        return f"{term.original} -> {term.thai}; near_miss={', '.join(misses)}; glossary={term.path.name}"
    return f"{term.original} -> {term.thai}; glossary={term.path.name}"


def output_has_glossary_translation(term: GlossaryTerm, text: str) -> bool:
    if term.thai in text:
        return True
    if term.category == "character" and " " in term.thai:
        first_name = term.thai.split()[0]
        return bool(first_name and first_name in text)
    return False


def covered_by_longer_source_term(term: GlossaryTerm, matched_terms: list[GlossaryTerm], translated_text: str) -> bool:
    """Avoid double-reporting subterms when the longer approved term is already rendered."""
    for longer in matched_terms:
        if longer is term:
            continue
        if len(longer.original) <= len(term.original):
            continue
        if term.original not in longer.original:
            continue
        if output_has_glossary_translation(longer, translated_text):
            return True
    return False


def scan_glossary_source_coverage(registry: dict, scoped: set[str] | None) -> list[Finding]:
    findings: list[Finding] = []
    for novel in registry.get("novels", []):
        slug = str(novel.get("slug", ""))
        root = WORKSPACE_ROOT / str(novel.get("folder", ""))
        raw_dir = str(novel.get("raw_dir", "03_Raw"))
        output_dir = str(novel.get("output_dir", "05_Output"))
        terms = approved_glossary_terms(root, findings)
        if not terms:
            continue
        for chapter in sorted(chapters_with_outputs(root, output_dir, slug, scoped)):
            source_text = source_text_for_chapter(root, raw_dir, chapter)
            if not source_text:
                continue
            matched_terms = [term for term in terms if source_contains_term(source_text, term.original)]
            if not matched_terms:
                continue
            surfaces = [
                ("final_output", final_output_path_for_chapter(root, output_dir, chapter)),
                ("moonread", reader_output_path_for_chapter(slug, chapter)),
            ]
            for surface, path in surfaces:
                if not path.exists():
                    continue
                translated_text = read_text(path)
                for term in matched_terms:
                    if output_has_glossary_translation(term, translated_text):
                        continue
                    if covered_by_longer_source_term(term, matched_terms, translated_text):
                        continue
                    findings.append(
                        Finding(
                            glossary_coverage_severity(term.category),
                            "glossary_coverage_missing",
                            str(path),
                            f"{surface}: source contains approved glossary term but output is missing thai_term",
                            format_near_miss_evidence(term, translated_text),
                        )
                    )
    return findings


def scan_approved_glossary_leakage(registry: dict, scoped: set[str] | None) -> list[Finding]:
    findings: list[Finding] = []
    for novel in registry.get("novels", []):
        slug = str(novel.get("slug", ""))
        root = WORKSPACE_ROOT / str(novel.get("folder", ""))
        terms = approved_glossary_terms(root, findings)
        if not terms:
            continue
        output_root = root / str(novel.get("output_dir", "05_Output"))
        reader_root = MOONREAD_ROOT / "content/generated/books" / slug / "chapters"
        for surface, surface_root in [("final_output", output_root), ("moonread", reader_root)]:
            for path in iter_markdown_files(surface_root, scoped):
                text = read_text(path)
                for term in terms:
                    if term.original not in text:
                        continue
                    escaped = re.escape(term.original)
                    patterns = [
                        rf"\({escaped}\)",
                        rf"\({escaped}\]",
                        rf"\[{escaped}\]",
                        rf"\*\*\[{escaped}\]\*\*",
                        rf"(?<![A-Za-z]){escaped}(?![A-Za-z])",
                    ]
                    if any(re.search(pattern, text) for pattern in patterns):
                        findings.append(
                            Finding(
                                "blocker",
                                "approved_glossary_leakage",
                                str(path),
                                f"{surface}: approved English remains: {term.original} -> {term.thai}",
                                term.path.name,
                            )
                        )
    return findings


ENGLISH_TOKEN_RE = re.compile(r"\b[A-Za-z][A-Za-z0-9'_-]{2,}(?:\s+[A-Za-z][A-Za-z0-9'_-]{2,}){0,3}\b")
ENGLISH_WHITELIST = {
    "http",
    "https",
    "www",
    "png",
    "jpg",
    "jpeg",
    "webp",
    "MoonRead",
}


def scan_suspicious_english(registry: dict, scoped: set[str] | None, *, max_examples: int = 80) -> list[Finding]:
    findings: list[Finding] = []
    seen: set[tuple[str, str]] = set()
    for novel in registry.get("novels", []):
        slug = str(novel.get("slug", ""))
        root = WORKSPACE_ROOT / str(novel.get("folder", ""))
        output_root = root / str(novel.get("output_dir", "05_Output"))
        reader_root = MOONREAD_ROOT / "content/generated/books" / slug / "chapters"
        for surface_root in [output_root, reader_root]:
            for path in iter_markdown_files(surface_root, scoped):
                text = read_text(path)
                for match in ENGLISH_TOKEN_RE.finditer(text):
                    token = match.group(0).strip()
                    if token in ENGLISH_WHITELIST or token.lower() in ENGLISH_WHITELIST:
                        continue
                    if re.fullmatch(r"ch\d+", token, re.IGNORECASE):
                        continue
                    key = (str(path), token)
                    if key in seen:
                        continue
                    seen.add(key)
                    severity = "major" if re.search(r"\([A-Za-z][^)]+\)|\[[A-Za-z][^\]]+\]", token) else "minor"
                    findings.append(
                        Finding(
                            severity,
                            "suspicious_english",
                            str(path),
                            "English token remains in product surface; review if intentional",
                            token,
                        )
                    )
                    if len(findings) >= max_examples:
                        return findings
    return findings


def summarize(findings: list[Finding]) -> dict[str, int]:
    counts = {"blocker": 0, "major": 0, "minor": 0, "info": 0}
    for finding in findings:
        counts[finding.severity] = counts.get(finding.severity, 0) + 1
    return counts


def write_reports(findings: list[Finding], *, scope: str, chapters: str | None) -> tuple[Path, Path]:
    REPORT_ROOT.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    base = f"sentinel_quality_{scope}_{stamp}"
    json_path = REPORT_ROOT / f"{base}.json"
    md_path = REPORT_ROOT / f"{base}.md"
    counts = summarize(findings)
    payload = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "scope": scope,
        "chapters": chapters or "all configured/current",
        "counts": counts,
        "safe_to_publish": counts.get("blocker", 0) == 0,
        "findings": [asdict(finding) for finding in findings],
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        f"# Sentinel Quality Report - {scope}",
        "",
        f"- Created: {payload['created_at']}",
        f"- Chapters: {payload['chapters']}",
        f"- Safe to publish: {'yes' if payload['safe_to_publish'] else 'no'}",
        f"- Blocker/Major/Minor/Info: {counts.get('blocker', 0)}/{counts.get('major', 0)}/{counts.get('minor', 0)}/{counts.get('info', 0)}",
        "",
        "## Next Action",
        "",
    ]
    if counts.get("blocker", 0):
        lines.append("- Stop publish. Repair blocker findings, then rerun Sentinel.")
    elif counts.get("major", 0):
        lines.append("- Inspect major findings before publish. Promote recurring true positives into blocker guardrails.")
    else:
        lines.append("- Product surface has no blocker findings under current Sentinel rules.")
    lines.extend(["", "## Findings", ""])
    if not findings:
        lines.append("- None")
    else:
        for finding in findings[:200]:
            evidence = f" Evidence: `{finding.evidence}`." if finding.evidence else ""
            lines.append(f"- **{finding.severity}** `{finding.category}` {finding.path}: {finding.message}.{evidence}")
        if len(findings) > 200:
            lines.append(f"- ... {len(findings) - 200} additional findings omitted from Markdown; see JSON.")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, md_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate Sentinel post-output quality report.")
    parser.add_argument("--scope", default="current", help="Short scope label for the report filename.")
    parser.add_argument("--novel", help="Novel slug or folder to scan, e.g. deep-sea-embers.")
    parser.add_argument("--chapters", help="Chapter scope like ch001-ch010 or ch001,ch005.")
    parser.add_argument("--fail-on", choices=["blocker", "major", "minor"], default="blocker")
    parser.add_argument("--skip-advisory-english", action="store_true")
    args = parser.parse_args(argv)

    scoped = parse_chapter_scope(args.chapters)
    registry = filter_registry(load_registry(), args.novel)
    findings: list[Finding] = []
    findings.extend(collect_existing_guardrails(scoped))
    findings = filter_findings_by_registry(findings, registry)
    findings.extend(scan_approved_glossary_leakage(registry, scoped))
    findings.extend(scan_glossary_source_coverage(registry, scoped))
    if not args.skip_advisory_english:
        findings.extend(scan_suspicious_english(registry, scoped))

    json_path, md_path = write_reports(findings, scope=args.scope, chapters=args.chapters)
    counts = summarize(findings)
    print(f"sentinel_quality_report: {md_path}")
    print(f"blocker/major/minor/info: {counts.get('blocker', 0)}/{counts.get('major', 0)}/{counts.get('minor', 0)}/{counts.get('info', 0)}")

    thresholds = {
        "blocker": counts.get("blocker", 0),
        "major": counts.get("blocker", 0) + counts.get("major", 0),
        "minor": counts.get("blocker", 0) + counts.get("major", 0) + counts.get("minor", 0),
    }
    return 1 if thresholds[args.fail_on] else 0


if __name__ == "__main__":
    raise SystemExit(main())
