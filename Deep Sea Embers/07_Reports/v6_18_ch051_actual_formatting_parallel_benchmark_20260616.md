# V6.18 Actual Formatting Parallel Benchmark

Run ID: `v6-18-benchmark-ch051-v1`

Benchmark target: `ch051`, fetched after the existing `ch001-ch050` production scope.

## Verdict

PASS for the narrow V6.18 runtime slice.

The benchmark proves that `formatting/openrouter` can run with limited parallelism when blocks are already QA-ready, without changing the conservative production defaults.

## Scope

- Chapter: `ch051`
- Blocks: 5 (`ch051-block-001` through `ch051-block-005`)
- Parallelized stage: `formatting` only
- Provider: `openrouter`
- Effective benchmark limit: `2`
- Config used for benchmark execution: temporary `.system/config.v6_18_benchmark.yaml`
- Production config after benchmark: `.system/config.yaml` remains `execution.concurrency_enabled: false`

## Preparation

The run was prepared in bounded stages:

1. `run --range ch051-ch051 --run-id v6-18-benchmark-ch051-v1 --stop-after glossary-scan`
2. Glossary approval gate closed through `07_Reports/v6_18_ch051_glossary_gate_20260616.md`
3. Per-block stage preparation was run only through QA:
   - `translate-literal`
   - `refine`
   - `qa`
4. All five blocks then had next pending stage `formatting`.

QA notes:

- `ch051-block-001`: QA passed retry 0
- `ch051-block-002`: QA passed retry 0
- `ch051-block-003`: QA passed retry 0
- `ch051-block-004`: QA passed after retry 1
- `ch051-block-005`: QA passed after retry 2
- No QA hard-fail was force-accepted.

## Benchmark Command

```powershell
novel-pipeline --config ".system/config.v6_18_benchmark.yaml" resume --run-id v6-18-benchmark-ch051-v1 --until-chapter ch051 --manual-action-mode stop
```

Observed runtime log:

```text
Formatting 5 ready blocks with limited parallelism.
```

Measured wall-clock:

- Parallel formatting wall-clock: `143.167` seconds
- Exit code: `0`

## Timing Comparison

Ledger formatting duration metadata:

| block_id | provider | mode | duration_seconds | parallel_limit |
| --- | --- | --- | ---: | ---: |
| ch051-block-001 | openrouter | provider | 140.842 | 2 |
| ch051-block-002 | openrouter | provider | 20.852 | 2 |
| ch051-block-003 | openrouter | provider | 41.682 | 2 |
| ch051-block-004 | openrouter | provider | 7.441 | 2 |
| ch051-block-005 | openrouter | provider | 42.371 | 2 |

Sequential estimate from the same provider durations:

- Sum of per-block formatting durations: `253.188` seconds
- Actual parallel wall-clock: `143.167` seconds
- Estimated saved time: `110.021` seconds
- Estimated reduction: `43.5%`

This is a bounded runtime result, not a broad approval to parallelize translation, refinement, or QA.

## Verification

Status after benchmark:

- `ch051`: `5/5` blocks complete
- Current failed blocks: none
- Historical failed records: `0`
- Final output exists: `05_Output/ch051/ch051.md`

Formatting ledger metadata:

- all five formatting records have `parallel_formatting: true`
- all five formatting records have `parallel_limit: 2`
- all five formatting records have `formatting_mode: provider`
- all five formatting records have `provider: openrouter`

Title gate:

- `04_Work/ch051/title.json` created through title provider workflow
- literal title provider: `openrouter` / `google/gemini-3-flash-preview`
- refine title provider: `openrouter` / `deepseek/deepseek-v4-flash`
- final heading: `# บทที่ 51: การดำเนินงานสองทาง`

Reports created:

- `07_Reports/v6_18_ch051_checkpoint_20260616.md`
- `07_Reports/v6_18_ch051_cleanliness_20260616.md`
- `07_Reports/v6_18_ch051_provider_usage_20260616.md`
- `07_Reports/v6_18_ch051_glossary_decisions_20260616.md`
- `07_Reports/v6_18_ch051_concurrency_after_format_20260616.md`

Validation commands:

- `python -m compileall novel_pipeline test_translation.py`: passed
- `python test_translation.py`: passed
- `python scripts/check_output_quality_guardrails.py`: passed
- `novel-pipeline --config ".system/config.yaml" preflight`: degraded only because the known working tree queue is dirty; providers are ready
- `git diff --check`: passed

## Rollback / Safety

- `.system/config.yaml` was not changed and remains conservative:
  - `execution.concurrency_enabled: false`
  - `execution.artifact_cache.mode: report_only`
  - `execution.pre_qa_guardrail.mode: report_only`
- The benchmark used a temporary config copy to enable concurrency only for this run.
- Runtime concurrency is not globally enabled by this benchmark.
- Cache skipping remains disabled.
- Pre-QA blocking remains report-only.

## Follow-Up Rule

V6.18 is complete for the first narrow runtime slice. Future speed work must remain staged:

1. keep formatting-only concurrency as the only proven runtime slice
2. do not enable global concurrency by default
3. do not parallelize QA without a separate cost/quality/failure benchmark
4. do not enable cache skip or Pre-QA blocking without separate approval
