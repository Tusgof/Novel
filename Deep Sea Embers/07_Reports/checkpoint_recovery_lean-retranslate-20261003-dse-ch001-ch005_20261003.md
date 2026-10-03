# Recovery Checkpoint - lean-retranslate-20261003-dse-ch001-ch005

- Order: `LEAN-RECOVERY-20261003-DSE`
- Novel: `deep-sea-embers`
- Requested recovery: `ch002` inside bounded run `ch001-ch005`
- Final run status: **blocked**
- Production outputs promoted: none

## Evidence and recovery

- Running-process check: no active process for this DSE run before recovery.
- Source/literal/refined/QA inspection identified the earliest broken stage as `literal_translation`: the prior literal checkpoint already rendered source role `二副` as `ต้นหน`.
- Removed only the stale ch002 run-local literal, refined, and failed-QA checkpoints.
- Resumed the same run ID with the configured Lean route.
- ch002 completed literal, refinement, formatting, and QA stages; QA recorded `PASS`.
- The regenerated literal and staged Markdown still contain `ต้นหน` for the `二副` role, so the semantic defect remains unresolved despite the QA pass. No force-accept or manual artifact patch was applied.
- All chapters `ch001-ch005` reached QA pass in the resumed run.

## Required gates

- ch002 deterministic guardrails: **failed** — paragraph 2 has 967 characters and paragraph 23 has 1085 characters.
- Full staged-range deterministic guardrails: **failed** — 13 dense-paragraph blockers across ch001-ch004.
- Blocking Sentinel: **failed** with `13 blocker / 0 major / 0 minor / 0 info`, all reported as dense-paragraph existing-guardrail findings.
- The pipeline stopped before promotion; later batches were not started.
- Provider metrics: 56 calls, 6 recorded provider failures; configured fallbacks allowed the run to continue to the Sentinel gate.

## Artifacts

- Run report: `Deep Sea Embers/04_Work/_lean_runs/lean-retranslate-20261003-dse-ch001-ch005/lean_run_report.json`
- ch002 staged output: `Deep Sea Embers/04_Work/_lean_runs/lean-retranslate-20261003-dse-ch001-ch005/_staged_output/ch002/ch002.md`
- Sentinel report: `07_Reports/sentinel_quality_lean-lean-retranslate-20261003-dse-ch001-ch005_20261003_084930.md`
- Sentinel JSON: `07_Reports/sentinel_quality_lean-lean-retranslate-20261003-dse-ch001-ch005_20261003_084930.json`

## Next safe action

Do not resume later batches. Resolve the semantic mapping for `二副` through the approved translation/glossary path and repair the dense-paragraph guardrail findings, then rerun ch002 QA and the blocking Sentinel before any promotion.
