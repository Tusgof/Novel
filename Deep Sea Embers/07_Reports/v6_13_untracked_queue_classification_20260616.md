# V6.13 Untracked Queue Classification - 2026-06-16

Purpose: classify the visible untracked queue without deleting, hiding, staging, or committing the queue itself.

No provider calls were made. No ledger, glossary, output, source, MoonRead, provider config, or pipeline runtime files were modified by this classification.

## Current Queue

Command used:

```powershell
git status --porcelain=v1 -z
```

Current untracked queue:

| group | count | disposition |
| --- | ---: | --- |
| `01_Glossary/*.md` | 46 | keep visible; review for dedicated glossary commit later |
| `07_Reports/*.md` | 19 | keep visible; review for archive/commit/discard decision later |
| other paths | 0 | none |

## Glossary Notes

Sampled glossary notes contain structured approved-term metadata, not obvious scratch text.

Examples:

| path | observed metadata |
| --- | --- |
| `01_Glossary/亚空间.md` | `status: approved`, `approved_by: codex_retranslate_glossary_gate` |
| `01_Glossary/亡灵法师.md` | `status: approved`, `approved_by: codex_retranslate_glossary_gate` |
| `01_Glossary/人偶小姐.md` | `status: approved`, `approved_by: codex_retranslate_glossary_gate` |
| `01_Glossary/基石.md` | `status: approved`, `approved_by: codex_ch001_ch050_v2_glossary_gate` |

Decision:

- Do not delete.
- Do not hide with `.gitignore`.
- Do not bulk commit without a glossary-specific review.
- Next safe action is a dedicated glossary queue review that checks each note for schema validity, duplicate/conflicting terms, and whether it belongs in source control.

## Reports

The 19 untracked reports are mostly OpenRouter, formatting, QA provider, and glossary approval evidence from June 2026.

Examples:

| path | heading |
| --- | --- |
| `07_Reports/format_spacing_probe_openrouter_20260609_040538.md` | `Format Spacing Probe - OpenRouter` |
| `07_Reports/glossary_approval_decisions_deep-sea-embers-retranslate-ch001-ch050-v2.md` | `Glossary Approval Decisions: deep-sea-embers-retranslate-ch001-ch050-v2` |
| `07_Reports/openrouter_bounded_block_probe_final_20260609.md` | `OpenRouter Bounded Block Probe` |
| `07_Reports/qa_provider_benchmark_20260610_strict_probe.md` | QA provider benchmark evidence |

Decision:

- Do not delete.
- Do not hide with `.gitignore`.
- Do not bulk commit blindly.
- Next safe action is a report evidence review that classifies each report as:
  - commit as durable evidence
  - move to `07_Reports/archive/`
  - discard only after explicit approval

## Recommended Next Step

Create a small follow-up milestone only if the user wants a clean `git status`:

1. Review the 46 glossary notes first because they may be source-of-truth approved terminology.
2. Commit valid glossary notes in a dedicated glossary commit.
3. Review the 19 reports separately and either commit/archive or discard with explicit approval.
4. Keep production/runtime work separate from this cleanup.

Until then, the safest state is to leave the queue visible and documented.
