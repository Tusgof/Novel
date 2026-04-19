---
name: novel-translation-qa
description: Interpret QA failures in the novel translation pipeline and route failed blocks back to refinement or escalation. Use when Codex needs to summarize QA findings, decide whether a block should retry, or explain a hard-fail state to the user.
---

# Novel Translation QA

Use this skill to interpret QA reports and communicate next actions.

## Expected Commands

QA and refinement are integrated stages within `run` and `resume`.
Use `novel-pipeline resume --run-id <id>` to resume from a QA failure.

## QA Policy

- `QA_MAX_RETRIES = 2` — each retry: re-run refiner with QA feedback → re-run QA
- After max retries: `hard_fail` → manual escalation
- Escalation options: **force-accept**, **skip**, **inspect-and-retry**
- Block does NOT proceed to formatting until QA passes or is force-accepted/skipped

## QA Report Structure

`QAReport` with `findings` (tuple of `QAFinding`).
Each finding: `severity`, `code`, `message`, `details`, `source_span`.
Rule-based checks: `missing_output`, `glossary_inconsistency`, `proper_name_drift`, `structure_mismatch`.
AI judge checks: `semantic_fidelity`, `omission_suspicion`, `addition_suspicion`.

## Runtime Artifacts

- `04_Work/<chapter_id>/<block_id>/literal.json` — literal drafts
- `04_Work/<chapter_id>/<block_id>/refined.json` — refined drafts
- `04_Work/<chapter_id>/<block_id>/qa.json` — QA reports
- `04_Work/<chapter_id>/<block_id>/formatted.json` — formatted output
- `06_Logs/run_ledger.jsonl` — stage history

## Guardrails

- Do not perform line alignment or semantic judging here.
- Do not modify runtime state directly; let the Python engine own pass/fail persistence.
