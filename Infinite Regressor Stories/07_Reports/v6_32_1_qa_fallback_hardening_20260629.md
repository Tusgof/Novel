# V6.32.1 QA Fallback Hardening Report

Status: stopped at gate; IRS is not production-ready yet.

## Scope

- Experiment vault: `Infinite Regressor Stories/04_Work/_experiments/v6_32_vault`
- Run IDs inspected: `irs-v6-32-insample-treatment-v2`, `irs-v6-32-insample-treatment-v3`
- Target: make QA fallback failures stop cleanly instead of cascading through unreliable workers.

## Changes Made

- Removed `codex` from automatic `qa_judge` fallback.
- Removed `qwen` from automatic `qa_judge` fallback after Windows headless qwen returned empty stdout with shell warnings.
- Added `openrouter_reasoning` fallback model `deepseek/deepseek-v4-pro` after primary `deepseek/deepseek-v4-flash`.
- Added provider timeout process-tree cleanup so timeout kills child processes.
- Added deterministic footnote marker preservation for source blocks ending with `Footnotes:` markers.
- Added regression tests for provider timeout handling, QA fallback policy, and source footnote marker preservation.

## Measured Results

`ch019-block-002` in `irs-v6-32-insample-treatment-v2` recovered:

- rerun from QA passed
- formatting completed
- no current failed blocks remained in v2 after the targeted rerun

`irs-v6-32-insample-treatment-v3` progressed farther but failed gate:

- records: 112
- completed blocks: 12
- completed chapters: `ch003`, `ch004`, `ch005`
- current failed block: `ch006-block-003`
- current failed stage: QA

Failure evidence:

- `deepseek/deepseek-v4-flash` reasoning returned empty assistant messages for `ch006-block-003` QA.
- `deepseek/deepseek-v4-pro` reasoning fallback also returned an empty assistant message for the same block.
- Earlier qwen fallback returned empty stdout with Windows/headless shell warnings, so qwen is not safe as automatic QA fallback in this environment.
- Codex fallback previously failed with quota, so Codex is not safe as automatic QA fallback either.

## Decision

V6.32.1 improved failure containment but did not make IRS pass the in-sample gate.

Do not run IRS out-of-sample, long production batches, or parallel batches yet.

## Next Safe Action

Run a QA-provider isolation probe for `ch006-block-003` before changing production routing again:

1. Build the exact QA prompt for `ch006-block-003`.
2. Test provider/model responses outside the full pipeline.
3. Record whether the issue is prompt-specific, model-specific, or OpenRouter-shim-specific.
4. Only after a QA provider passes the probe, rerun `ch006-block-003` from QA.
5. Resume `irs-v6-32-insample-treatment-v3` only after `ch006-block-003` has no current failed block.

## Validation

- `python -m compileall novel_pipeline`: passed
- `python test_translation.py`: passed
- Latest status confirms the run stops at `ch006-block-003` rather than cascading into Codex or qwen.
