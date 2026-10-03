# Checkpoint Report - Direct QA Repair DSE ch002

- Order: `LEAN-DIRECT-QA-REPAIR-20261003-DSE-CH002`
- Novel: `deep-sea-embers`
- Bounded run: `lean-retranslate-20261003-dse-ch001-ch005`
- Scope completed: `ch001-ch005` (affected chapter: `ch002`)
- Final run status: **complete**

## Source-backed repair

- The earliest defect was in the ch002 literal artifact: source role `二副` was rendered as the navigator term `ต้นหน`.
- Replaced that one aligned occurrence with `รองต้นเรือ` in the literal, refined, formatted, staged, and promoted ch002 artifacts.
- No other `ต้นหน` occurrence was changed.
- Reflowed only the 13 paragraphs previously reported by deterministic guardrails, using whitespace boundaries and preserving normalized wording exactly.
- No whole translation rerun, force-accept, provider routing change, commit, push, publish, or scope expansion was used.

## Gates

- ch002 QA: **pass** through the configured QA route after the repair.
- All five chapter QA gates: **pass**.
- Staged deterministic guardrails before resume: **pass**.
- Staged blocking Sentinel before resume: **0 blocker / 0 major / 0 minor / 0 info**.
- Final promoted-output deterministic guardrails: **pass**.
- Final blocking Sentinel: **0 blocker / 0 major / 0 minor / 0 info**.
- Promoted outputs: `Deep Sea Embers/05_Output/ch001-ch005/` chapter files (5 files).

## Resume evidence

- Provider calls: `58` total; `literal_translation=33`, `refinement=6`, `qa_judge=14`, `term_harvest=5`.
- Compared with the blocked run, only QA increased (`12` to `14`); literal, refinement, and harvest counts were unchanged.
- ch002 reused literal, refinement, formatting, and term-harvest checkpoints; QA was rerun.
- Configured primary QA route had empty-response incidents, but fallback QA succeeded; no unresolved provider failure remained.

## Spot check

- `ch001`: max paragraph 763 characters; required name present; opening/middle/ending inspected.
- `ch002`: max paragraph 887 characters; `รองต้นเรือ` present and stale `ต้นหน` absent; opening/middle/ending inspected.
- `ch003`: max paragraph 726 characters; required name present; opening/middle/ending inspected.
- `ch004`: max paragraph 843 characters; required name present; opening/middle/ending inspected.
- `ch005`: max paragraph 859 characters; required name present; opening/middle/ending inspected.

## Artifacts

- Run report: `Deep Sea Embers/04_Work/_lean_runs/lean-retranslate-20261003-dse-ch001-ch005/lean_run_report.json`
- Final Sentinel report: `Deep Sea Embers/07_Reports/sentinel_quality_direct-qa-repair-final-dse-ch001-ch005_20261003_093513.md`
- Final Sentinel JSON: `Deep Sea Embers/07_Reports/sentinel_quality_direct-qa-repair-final-dse-ch001-ch005_20261003_093513.json`
- This checkpoint: `Deep Sea Embers/07_Reports/checkpoint_direct-qa-repair-dse-ch002_lean-retranslate-20261003-dse-ch001-ch005.md`

## Prevention

- Keep the source-backed nautical-role mapping explicit in future repairs: `二副` maps to `รองต้นเรือ`; do not substitute the navigator role.
- Run the deterministic paragraph-density guardrail on staged output before resuming a bounded production run.
