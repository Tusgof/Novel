# V6.32 IRS Experiment Completion Report

- Created: 2026-06-29T09:57:58.687966+00:00
- Verdict: PASS for mandatory IRS setup experiment; NOT approved for long parallel production yet.
- Scope: 20 chapters total, 10 in-sample and 10 out-of-sample.
- In-sample: ch003, ch004, ch005, ch006, ch007, ch008, ch009, ch018, ch019, ch020
- Out-of-sample: ch021, ch023, ch026, ch032, ch034, ch035, ch038, ch040, ch044, ch055
- Experiment vault: Infinite Regressor Stories/04_Work/_experiments/v6_32_vault

## Provider Isolation Result

- Original blocker: ch006-block-003 QA. OpenRouter reasoning Flash and Pro returned empty assistant messages on the full QA prompt.
- Probe result: deepseek/deepseek-v4-flash without reasoning returned PASS quickly; google/gemini-3-flash-preview also returned PASS; reasoning Flash and reasoning Pro returned empty assistant messages.
- Experiment decision: isolated vault QA route changed to non-reasoning OpenRouter deepseek/deepseek-v4-flash with Gemini Flash fallback.

| probe | returncode | seconds | stdout_len | note |
| --- | ---: | ---: | ---: | --- |
| flash_reasoning | 1 | 76.26 | 0 | OpenRouter shim error after 74.52s: OpenRouter returned an empty assistant messa |
| flash_no_reasoning | 0 | 4.06 | 5 | PASS: |
| pro_reasoning | 1 | 23.04 | 0 | OpenRouter shim error after 21.48s: OpenRouter returned an empty assistant messa |
| gemini_flash | 0 | 4.68 | 70 | PASS: The translation follows all glossary terms and style guidelines. |

## Run Metrics

### irs-v6-32-insample-treatment-v3

- records: 264
- completed_blocks: 34
- qa_completed: 36
- historical_failed_records: 9
- hard_fail_records: 2
- local_recovery_refines: 7

### irs-v6-32-oos-v1

- records: 215
- completed_blocks: 32
- qa_completed: 32
- historical_failed_records: 1
- hard_fail_records: 1
- local_recovery_refines: 5

## Repairs During Completion

- ch006-block-003: recovered by switching QA route away from reasoning mode, then rerunning QA/format.
- ch008-block-002: stale provider process after timeout; killed only the stale resume/shim process, then reran formatting.
- ch019-block-001: QA false hard-fail after the opening roar was already present; reran QA and passed.
- ch040-block-004: stale provider process after timeout; killed only the stale resume/shim process, then reran QA/format.
- ch044-block-001: repaired numeric drift from cycles 110-115 to 10-15, then reran QA/format.
- ch009-block-003: repeated provider runaway/truncation around the Saintess greeting. Rerunning refine reproduced the issue, so a source-bounded deterministic tail repair was applied and QA/format reran successfully.

## Deterministic Verification

- 20/20 final chapter outputs exist in the experiment vault.
- Current failed blocks: none for both in-sample and out-of-sample runs.
- Manual actions needed: none after recovery.
- Custom scoped output audit passed: no provider/meta text, no Han body text, no question-placeholder mojibake, no quote-only lines, no long repeated-character run, and no low output/source length ratio.
- Glossary corruption repair: 62 incorrectly encoded experiment-only notes were deleted; the out-of-sample decision report now rejects all new scan terms for this isolated experiment and relies on existing IRS glossary/title sidecars.

## Decision

- V6.32 IRS setup experiment is complete for IRS.
- The pipeline is safe enough for the next bounded IRS production pilot, but not for long unmonitored parallel production.
- Recommended next execution mode: sequential bounded batches or small chapter-level batches with strict timeout cleanup and deterministic output audit after each batch.
- Do not enable broad translation/refinement/QA parallelism yet. Retry/recovery incidence is still too high.

## Follow-up Guardrails

- Promote long repeated-character detection to the shared output guardrail before scaling IRS.
- Keep reasoning-enabled OpenRouter QA out of IRS long prompts unless a later probe proves it no longer returns empty assistant messages.
- Keep glossary note creation UTF-8-safe; do not create Thai glossary notes through a shell path that may encode Thai as question marks.
- Add isolated-vault Sentinel support or a scoped experiment-output audit command, because registry-based Sentinel scans the real novel vault, not the experiment vault.
- V6.32G remains deferred: repeat the experiment protocol with DSE and HGD only after user approval.
