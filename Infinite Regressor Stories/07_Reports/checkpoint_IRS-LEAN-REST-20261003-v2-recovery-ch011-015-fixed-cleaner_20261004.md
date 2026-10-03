# Lean checkpoint report - IRS ch011-ch015

- Order: `IRS-LEAN-REST-20261003-v2`
- Ownership: Infinite Regressor Stories `ch011-ch015` only. `ch016-ch020` are explicitly excluded and were not started.
- Run: `IRS-LEAN-REST-20261003-v2-recovery-ch011-015-fixed-cleaner`
- Runtime status: `complete`
- Promotion: ch011, ch012, ch013, ch014, and ch015 promoted; no chapters quarantined.
- Runtime report: [lean_run_report.json](../04_Work/_lean_runs/IRS-LEAN-REST-20261003-v2-recovery-ch011-015-fixed-cleaner/lean_run_report.json)
- No routing, threshold, glossary-policy, publication, Git, registry, or MoonRead changes were made.

## Cleaner recovery and trace evidence

The shared refine cleaner was fixed before the final QA pass. Trace inspection found no source ASCII `---` scene breaks in ch011-ch015, and the source-backed list lines were retained in the repaired artifacts. In particular, ch012 retains both source `*` lines, ch014 retains the `- S.` chat marker and its chat lines, and the ch015 list lines remain present.

The original ch011 refinement trace was the earliest broken stage: the provider returned an empty stdout (`stdout_chars: 0`, return code 1, `finish_reason=length`). Refinement was rerun from that stage with the healthy provider stdout and fixed cleaner. The repaired ch011 refined artifact now contains the complete ending through the Busan Station/Sim Ah-ryeon passage and final question; it does not stop at the earlier `ที่พัก` cut.

Source-backed local repairs were then applied before QA:

- ch011: restored `(Advanced)`, restored both `Team Leader Ju-ho` titles, and reflowed dense paragraphs/headings.
- ch012: corrected the Saintess feminine register and cleaned the affected heading/list formatting.
- ch013: merged the split dialogue, corrected the five narrator pronouns, and reflowed the affected paragraph.
- ch014: preserved the chat/list lines and repaired the affected list and heading layout.
- ch015: reflowed dense paragraphs and cleaned the affected heading/list layout.

The approved semantic rendering of `iJoinedToday` as `เพิ่งสมัครวันนี้` was retained.

## Chapter gates

| Chapter | QA | Formatting/guardrails | Blocking Sentinel | Action |
| --- | --- | --- | --- | --- |
| ch011 | PASS | PASS | 0 blocker / 0 major / 0 minor / 0 info | Promoted |
| ch012 | PASS (configured fallback route) | PASS | 0 / 0 / 0 / 0 | Promoted |
| ch013 | PASS (configured fallback route) | PASS | 0 / 0 / 0 / 0 | Promoted |
| ch014 | PASS (configured fallback route) | PASS | 0 / 0 / 0 / 0 | Promoted |
| ch015 | PASS | PASS | 0 / 0 / 0 / 0 | Promoted |

The deterministic guardrail command
`python -X utf8 scripts/check_output_quality_guardrails.py --config "Infinite Regressor Stories/.system/config.yaml" --chapters ch011-ch015`
returned `output_quality_guardrails: passed`.

The final stage-only blocking Sentinel returned `0/0/0/0` (blocker/major/minor/info), `failed: false`, and `safe_to_publish: true`:

- [JSON report](../../07_Reports/sentinel_quality_lean-IRS-LEAN-REST-20261003-v2-recovery-ch011-015-fixed-cleaner-postcheck-final_20261003_185847.json)
- [Markdown report](../../07_Reports/sentinel_quality_lean-IRS-LEAN-REST-20261003-v2-recovery-ch011-015-fixed-cleaner-postcheck-final_20261003_185847.md)

The runtime also emitted zero-finding per-chapter blocking Sentinel reports for ch011-ch015.

## Provider incidents

The bounded run made 51 provider calls and recorded 7 recoverable provider failures. They were retry/fallback incidents (the ch011 empty refinement response, a ch012 refinement response, and QA retry failures on ch012-ch014); configured routes completed the affected stages. No global provider exhaustion occurred, and no route or threshold was changed.

## Five-chapter spot check

All five promoted outputs were inspected at title, opening, middle, ending, dialogue/thought formatting, glossary/name consistency, and paragraph density:

- ch011: `(Advanced)` title, both Team Leader titles, and the complete ending; maximum paragraph 513 characters.
- ch012: both source list lines and the female Saintess register; maximum paragraph 537 characters.
- ch013: merged dialogue, corrected narrator pronouns, and the ending footnote; maximum paragraph 492 characters.
- ch014: preserved chat/list lines including `- S.`; maximum paragraph 534 characters.
- ch015: both source-backed list lines and the ending footnote; maximum paragraph 576 characters.

No provider metadata, truncation marker, or source omission was found in the promoted outputs. The next safe action is Inspector acceptance; ch016-ch020 remain outside this order.
