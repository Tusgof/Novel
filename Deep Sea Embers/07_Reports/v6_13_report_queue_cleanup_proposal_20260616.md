# V6.13 Report Queue Cleanup Proposal - 2026-06-16

Purpose: turn the visible untracked report queue into a low-risk cleanup decision without moving, deleting, staging, or committing the queued reports themselves.

No provider calls were made. No ledger, glossary notes, source files, output files, MoonRead files, provider config, or runtime artifacts were modified.

## Current Queue

Visible untracked report queue:

- 19 report files under `07_Reports/`
- 5 final/decision evidence reports
- 11 intermediate benchmark/probe reports
- 3 formatting probe reports

Prior classification:

- `07_Reports/v6_13_report_queue_review_20260616.md`

## Recommended Cleanup Path

Recommended order:

1. Commit the 5 durable evidence reports in one report-only commit.
2. Leave the 14 intermediate/probe reports visible until the durable evidence commit is verified.
3. In a separate archive-only step, move the 14 intermediate/probe reports to `07_Reports/archive/20260609_openrouter_qa_formatting/` if the user wants a cleaner root report directory.
4. Do not delete any report unless the user explicitly approves deletion after archive verification.

This keeps evidence available while reducing the chance that cleanup hides useful provider-routing history.

## Durable Evidence To Commit First

| path | why keep |
| --- | --- |
| `07_Reports/glossary_approval_decisions_deep-sea-embers-retranslate-ch001-ch050-v2.md` | documents glossary approval decisions for the full DSE `ch001-ch050` retranslation |
| `07_Reports/openrouter_provider_benchmark_final_20260609.md` | final OpenRouter provider benchmark decision evidence |
| `07_Reports/openrouter_bounded_block_probe_final_20260609.md` | final bounded block probe evidence before routing changes |
| `07_Reports/openrouter_provider_routing_proposal_20260609.md` | routing proposal connected to the final benchmark/probe reports |
| `07_Reports/qa_provider_benchmark_20260610_strict_probe.md` | strict QA probe evidence showing OpenRouter `deepseek/deepseek-v4-flash` reasoning was not enough to fully replace current QA without caution |

Why this is useful:

- These files explain current provider-routing decisions.
- They document that key/provider handling did not write bearer tokens to artifacts.
- They preserve why QA routing stayed conservative after strict probe failures.
- They are durable evidence, not transient logs.

## Intermediate / Probe Reports To Archive Later

Archive-only candidate path:

```text
07_Reports/archive/20260609_openrouter_qa_formatting/
```

Candidate files:

- `07_Reports/openrouter_provider_benchmark_auth_gate_20260609.md`
- `07_Reports/openrouter_provider_replacement_experiment_20260609.md`
- `07_Reports/openrouter_bounded_block_probe_20260609_033555.md`
- `07_Reports/openrouter_provider_benchmark_20260609_024241.md`
- `07_Reports/openrouter_provider_benchmark_20260609_025600.md`
- `07_Reports/openrouter_provider_benchmark_20260609_025657.md`
- `07_Reports/openrouter_provider_benchmark_20260609_025818.md`
- `07_Reports/qa_provider_benchmark_20260609_134339.md`
- `07_Reports/qa_provider_benchmark_20260609_134420.md`
- `07_Reports/qa_provider_benchmark_20260609_142846.md`
- `07_Reports/qa_provider_benchmark_20260609_142859.md`
- `07_Reports/format_style_probe_openrouter_20260609_035932.md`
- `07_Reports/format_style_probe_openrouter_20260609_040051.md`
- `07_Reports/format_spacing_probe_openrouter_20260609_040538.md`

Why archive instead of delete:

- They may still explain route selection, timing variation, failed attempts, and formatting decisions.
- Formatting reports remain relevant while `C:\Users\ASUS\Downloads\good format.md` is an active quality reference.
- Archive keeps `git status` cleaner without destroying audit history.

## Stop Rules

- Keep glossary cleanup separate from report cleanup.
- Do not mix report cleanup with runtime/provider/code changes.
- Do not delete any report without explicit user approval.
- If a report is referenced by `PROJECT_BRAIN.md`, `IMPLEMENT_PLAN.md`, or another tracked report, keep or archive it; do not discard it.

## Acceptance Criteria For Future Cleanup

Durable-evidence commit is done when:

- only the 5 durable evidence reports are staged
- `git diff --cached --stat` shows only those reports
- no provider calls or pipeline commands run
- `git status --short` still shows the remaining queue but no unintended tracked modifications

Archive-only follow-up is done when:

- exactly the 14 intermediate/probe reports move under `07_Reports/archive/20260609_openrouter_qa_formatting/`
- no report contents are edited
- docs referencing final reports still resolve
- `git diff --summary` shows renames/moves only for the archive step
