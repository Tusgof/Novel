# Checkpoint Report — IRS Lean Recovery v2

- Order: `IRS-LEAN-RECOVERY-20261003-v2`
- Run: `LEAN-RETRANSLATE-20261003-IRS-b01`
- Novel and range: Infinite Regressor Stories, `ch001–ch005`
- Runtime status: `complete`
- Runtime report: `Infinite Regressor Stories/04_Work/_lean_runs/LEAN-RETRANSLATE-20261003-IRS-b01/lean_run_report.json`
- Promotion: all five chapters promoted; no chapters quarantined
- Provider metrics: 49 calls, 5 provider failures, 3881.734 provider seconds; configured fallback routes completed the affected calls

## Chapter gates

| Chapter | QA | Formatting/guardrails | Blocking Sentinel | Action |
| --- | --- | --- | --- | --- |
| ch001 | PASS | PASS | 0 blockers | Promoted |
| ch002 | PASS | PASS | 0 blockers | Promoted |
| ch003 | PASS | PASS | 0 blockers | Promoted |
| ch004 | PASS | PASS | 0 blockers | Promoted |
| ch005 | PASS | PASS | 0 blockers | Promoted |

The deterministic guardrail command `python scripts/check_output_quality_guardrails.py --config "Infinite Regressor Stories/.system/config.yaml" --chapters "ch001-ch005"` returned `output_quality_guardrails: passed`.

The final blocking Sentinel is [sentinel_quality_lean-LEAN-RETRANSLATE-20261003-IRS-b01_20261003_113437.json](../../07_Reports/sentinel_quality_lean-LEAN-RETRANSLATE-20261003-IRS-b01_20261003_113437.json) with companion Markdown report [sentinel_quality_lean-LEAN-RETRANSLATE-20261003-IRS-b01_20261003_113437.md](../../07_Reports/sentinel_quality_lean-LEAN-RETRANSLATE-20261003-IRS-b01_20261003_113437.md): blocker/major/minor/info `0/0/7/0`, `safe_to_publish: true`. The seven minors are advisory English-token reviews (`Resume`, `The World`, `Will and Representation`, `noumenon`, `The Scream`, `LiteraryGirl`, and `dolLHoUse`).

## Recovery

- ch001: marked the existing `บทที่ 1` body title with italic Markdown so the title is not duplicated under the H1. The source and refined text were unchanged. The repaired output keeps the Scho/show line as `กล้ามเนื้อพวกนั้นของแกมีไว้โชว์หรือไง?` and does not address Old Man Scho as `ตาแก่โช` in that line.
- ch005: split the existing formatted paragraph after `มินต์ล้วนๆ` at a source-backed sentence boundary. The dense paragraph fell from 714 to 550 characters; no source or refined meaning changed.
- ch002–ch004: reused the earlier deterministic title and paragraph-density repairs. Their checkpoints remained content-valid and passed the same gates.
- All repaired formatted checkpoints passed the runtime formatter validator before resume. No force-accept, routing change, publish, commit, or push was used.

## Spot check

All five promoted files under `Infinite Regressor Stories/05_Output` were sampled at the title, opening, middle, and ending. Paragraph maxima were: ch001 `569`, ch002 `509`, ch003 `391`, ch004 `557`, and ch005 `550` characters. Dialogue and ellipsis lines remain present and readable; no truncation or provider metadata was found. Approved-name checks include `อาร์เธอร์ โชเพนเฮาเออร์` and `ตาแก่โช` in ch001 and `ผู้กล้า` in ch005.

## Prevention

The failure class was deterministic output formatting: title-like body duplication and paragraph density. The recovery now relies on JSON-aware formatted-checkpoint repairs, the runtime content-preserving validator, the scoped output guardrail, and the blocking Sentinel before promotion. The prior partial report remains historical; this report is the completed recovery checkpoint.
