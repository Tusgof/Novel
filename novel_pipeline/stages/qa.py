from __future__ import annotations

import re

from novel_pipeline.prompts import PromptStore
from novel_pipeline.providers.base import ProviderRunner, ensure_provider_response
from novel_pipeline.text_utils import split_sentences, validate_text_script
from novel_pipeline.types import AppConfig, GlossaryEntry, LiteralDraft, ProviderRequest, QAFinding, QAReport, RefinedDraft, TextBlock


def run_qa_stage(
    *,
    config: AppConfig,
    block: TextBlock,
    literal_draft: LiteralDraft,
    refined_draft: RefinedDraft,
    glossary_subset: list[GlossaryEntry],
    provider_runner: ProviderRunner,
    model: str = "",
    retry_count: int,
) -> QAReport:
    findings = run_rule_checks(literal_draft=literal_draft, refined_draft=refined_draft, glossary_subset=glossary_subset)
    blocking_findings = [item for item in findings if item.severity == "error"]
    if blocking_findings:
        return QAReport(
            block_id=block.block_id,
            chapter_id=block.chapter_id,
            passed=False,
            findings=tuple(findings),
            feedback="; ".join(item.message for item in blocking_findings),
            retry_count=retry_count,
            judge_provider="rules",
        )
    prompt_store = PromptStore(config.workspace.prompts)
    prompt = prompt_store.render(
        "qa_judge",
        source_block=block.source_text,
        literal_draft=literal_draft.to_dict(),
        refined_draft=refined_draft.to_dict(),
        glossary_subset=[entry.to_dict() for entry in glossary_subset],
    )
    feedback = ""
    response = provider_runner.run_with_retry(
        ProviderRequest(
            prompt=prompt,
            provider=provider_runner.spec.name,
            stage="qa_judge",
            model=model,
        )
    )
    ensure_provider_response(response)
    ai_findings, feedback = parse_ai_feedback(response.stdout)
    findings.extend(ai_findings)
    blocking_findings = [item for item in findings if _is_blocking_finding(item)]
    return QAReport(
        block_id=block.block_id,
        chapter_id=block.chapter_id,
        passed=not blocking_findings,
        findings=tuple(findings),
        feedback=feedback or "; ".join(item.message for item in blocking_findings or findings),
        retry_count=retry_count,
        judge_provider=provider_runner.spec.name,
    )


def run_rule_checks(*, literal_draft: LiteralDraft, refined_draft: RefinedDraft, glossary_subset: list[GlossaryEntry]) -> list[QAFinding]:
    findings: list[QAFinding] = []
    refined_text = refined_draft.refined_text.strip()
    if not refined_text:
        findings.append(QAFinding(severity="error", code="missing_output", message="Refined output is empty."))
    else:
        try:
            validate_text_script(refined_text, "th")
        except ValueError as e:
            findings.append(QAFinding(severity="error", code="mojibake", message=f"Text appears to be mojibake: {e}"))
    if _looks_like_provider_meta(refined_text):
        findings.append(QAFinding(severity="error", code="provider_meta_leakage", message="Refined output looks like provider status/error text."))
    if _contains_cjk(refined_text):
        findings.append(QAFinding(severity="error", code="untranslated_source_leakage", message="Refined output still contains Chinese/Japanese/Korean source characters."))
    if _contains_xianxia_drift(refined_text):
        findings.append(QAFinding(severity="warning", code="genre_drift", message="Refined output may have drifted into wuxia/xianxia diction."))
    literal_sentence_count = len(literal_draft.sentence_pairs)
    refined_sentence_count = len(split_sentences(refined_text))
    if refined_sentence_count == 0:
        findings.append(QAFinding(severity="error", code="structure_mismatch", message="Refined output has no sentence boundaries."))
    elif literal_sentence_count and refined_sentence_count < max(1, literal_sentence_count // 2):
        findings.append(QAFinding(severity="warning", code="sentence_drop", message="Refined output may have dropped too many sentence boundaries."))
    for entry in glossary_subset:
        expected_terms = [entry.thai_term, *entry.aliases]
        if entry.thai_term and not any(term and term in refined_text for term in expected_terms):
            findings.append(QAFinding(severity="warning", code="glossary_inconsistency", message=f"Expected term not found: {entry.thai_term}"))
    return findings


def _looks_like_provider_meta(text: str) -> bool:
    lowered = text.lower()
    if re.search(r"\b(hit your limit|usage limit|rate limit|quota|too many requests|resets \d|as an ai|i can't|i cannot)\b", lowered):
        return True
    if len(text) < 240 and re.search(r"\b(error|failed|exception|traceback|unauthorized|permission denied)\b", lowered):
        return True
    return False


def _contains_cjk(text: str) -> bool:
    return bool(re.search(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]", text))


def _contains_xianxia_drift(text: str) -> bool:
    return any(term in text for term in ("สำนัก", "ขั้นพลัง", "ปราณ", "วิชาเทพ", "เคล็ดวิชา", "บ่มเพาะ"))


def _is_blocking_finding(finding: QAFinding) -> bool:
    return finding.severity == "error" or finding.code == "ai_judge"


def parse_ai_feedback(stdout: str) -> tuple[list[QAFinding], str]:
    findings: list[QAFinding] = []
    feedback_lines: list[str] = []
    for raw_line in stdout.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        lowered = line.lower()
        if lowered.startswith(("fail", "issue", "finding", "warning", "error")):
            findings.append(QAFinding(severity="warning", code="ai_judge", message=line))
        else:
            feedback_lines.append(line)
    return findings, "\n".join(feedback_lines).strip()
