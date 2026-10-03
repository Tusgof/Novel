# Checkpoint Report - lean-retranslate-20261003-dse-ch001-ch005

- Order: `LEAN-RETRANSLATE-20261003-DSE`
- Novel: `deep-sea-embers`
- Pipeline: Lean production
- Requested range: `ch001-ch005`
- Run status: **blocked**
- Started: `2026-10-03T07:52:25.961039+00:00`
- Finished: `2026-10-03T08:01:10.577123+00:00`

## Gates and execution

- Source/title preflight: passed for `ch001-ch020` after the scoped `ch016/title.json` glossary correction (`灵界行走` -> `การเดินทางในมิติวิญญาณ`).
- Dry-run source validation: passed for all four requested batches (`ch001-ch005`, `ch006-ch010`, `ch011-ch015`, `ch016-ch020`).
- Completed before stop: `ch001` (5 blocks; QA passed; staged only).
- Stop chapter: `ch002`.
- Stop reason: hard QA failure; no force-accept or manual repair applied.
- Failure: source role `二副` (second mate) was rendered as `ต้นหน` (navigator), changing the nautical rank.
- Provider incidents: 18 provider calls, 2 recorded failures. The primary QA route returned an empty assistant message (`finish_reason=length`); configured fallback QA passed for `ch001`.
- Sentinel: not run because the batch stopped at the hard QA gate.
- Output guardrails and spot-check: not run because the batch stopped at the hard QA gate.
- Promoted production outputs: none.

## Artifacts

- Machine checkpoint: `Deep Sea Embers/04_Work/_lean_runs/lean-retranslate-20261003-dse-ch001-ch005/lean_run_report.json`
- Staged `ch001` output remains under the run checkpoint directory and was not promoted.

## Next safe action

Repair or rerun the affected `ch002` translation from the earliest failed stage using the configured route, then resume this exact bounded run only after the nautical-role QA issue is resolved. Do not start later chapter batches while this run is blocked.
