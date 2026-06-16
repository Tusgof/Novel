# V6.13 Report Queue Review - 2026-06-16

Purpose: review the 19 visible untracked report files without moving, deleting, staging, or committing those report files.

No provider calls were made. No ledger, glossary, source, output, MoonRead, provider config, or pipeline runtime files were modified.

## Summary

| group | count | recommended disposition |
| --- | ---: | --- |
| final / decision evidence | 5 | commit or keep as durable evidence after one focused report commit |
| intermediate benchmark/probe evidence | 11 | archive under `07_Reports/archive/` or commit only if needed for audit trace |
| formatting probe evidence | 3 | archive or keep with the final formatting decision evidence |

This review does not approve deleting any report. Deletion should require explicit user approval after confirming the report is superseded and not referenced by docs.

## Recommended Durable Evidence

These reports appear to hold final or decision-level evidence and should be considered first for a dedicated commit:

| path | reason |
| --- | --- |
| `07_Reports/glossary_approval_decisions_deep-sea-embers-retranslate-ch001-ch050-v2.md` | documents glossary approval decisions for the full DSE retranslation run |
| `07_Reports/openrouter_provider_benchmark_final_20260609.md` | final OpenRouter benchmark decision evidence |
| `07_Reports/openrouter_bounded_block_probe_final_20260609.md` | final bounded block probe evidence |
| `07_Reports/openrouter_provider_routing_proposal_20260609.md` | routing proposal tied to the final benchmark/probe reports |
| `07_Reports/qa_provider_benchmark_20260610_strict_probe.md` | strict QA probe evidence for the later QA-routing decision |

## Intermediate Evidence

These files look like earlier attempts or intermediate benchmark/probe runs. They may be useful for audit history, but should not be mixed into runtime/code commits.

| path | reason |
| --- | --- |
| `07_Reports/openrouter_provider_benchmark_auth_gate_20260609.md` | authentication failure gate; useful context but superseded by later successful benchmark |
| `07_Reports/openrouter_provider_replacement_experiment_20260609.md` | experiment design; useful context but not final decision |
| `07_Reports/openrouter_bounded_block_probe_20260609_033555.md` | preliminary probe before final rescored report |
| `07_Reports/openrouter_provider_benchmark_20260609_024241.md` | early benchmark attempt |
| `07_Reports/openrouter_provider_benchmark_20260609_025600.md` | early benchmark attempt |
| `07_Reports/openrouter_provider_benchmark_20260609_025657.md` | early benchmark attempt |
| `07_Reports/openrouter_provider_benchmark_20260609_025818.md` | larger but still superseded benchmark attempt |
| `07_Reports/qa_provider_benchmark_20260609_134339.md` | small QA benchmark attempt |
| `07_Reports/qa_provider_benchmark_20260609_134420.md` | QA benchmark attempt before later candidate set |
| `07_Reports/qa_provider_benchmark_20260609_142846.md` | small QA benchmark attempt |
| `07_Reports/qa_provider_benchmark_20260609_142859.md` | later QA benchmark run before strict probe |

## Formatting Probe Evidence

These reports are small and related to choosing AI formatting behavior.

| path | reason |
| --- | --- |
| `07_Reports/format_style_probe_openrouter_20260609_035932.md` | failed/early formatting probe |
| `07_Reports/format_style_probe_openrouter_20260609_040051.md` | successful formatting probe |
| `07_Reports/format_spacing_probe_openrouter_20260609_040538.md` | spacing-specific formatting probe |

Recommended handling:

- Keep or archive them with formatting evidence.
- Do not delete them while HGD formatting and `good format.md` remain active quality references.

## Recommended Next Step

If the user wants a cleaner `git status`, do this as a dedicated cleanup milestone:

1. Commit the 5 durable evidence reports in one report-only commit, or move all 19 reports to `07_Reports/archive/` in one archive-only commit.
2. Keep glossary-note cleanup separate from report cleanup.
3. Do not mix report cleanup with provider routing, translation runs, MoonRead generation, or code changes.
4. Do not discard any report without explicit approval.

Until then, the safest state is to leave the 19 reports visible and documented.
