# V6.18 Benchmark Command Packet - 2026-06-16

Purpose: prepare the exact approval, precheck, command shape, stop rules, and evidence requirements for the V6.18 speed benchmark without running it.

No provider calls were made. No pipeline commands were run. No ledger, glossary notes, source files, output files, MoonRead files, provider config, or runtime artifacts were modified.

## Current Gate

V6.18 remains gated.

Do not run a benchmark until the user explicitly approves:

```text
Approve V6.18 formatting/openrouter concurrency=2 benchmark on one bounded chapter after ch050.
```

## Important Implementation Gap

Inspection on 2026-06-16 found:

- `.system/config.yaml` defines:
  - `execution.concurrency_enabled: false`
  - `execution.stage_concurrency.formatting: 2`
- `novel_pipeline/types.py` parses the execution policy.
- `novel_pipeline/reports.py` can generate read-only concurrency projections.
- `novel_pipeline/pipeline.py` does not currently use `ExecutionPolicy.effective_stage_limit()` or a parallel executor for stage runtime.

Implication:

- A real `formatting/openrouter concurrency=2` benchmark cannot be produced by simply changing YAML.
- Before any true benchmark, the project needs either:
  1. a minimal approved runtime implementation for formatting-stage parallelism only, or
  2. confirmation that a separate benchmark harness exists and is intentionally outside `pipeline.py`.

Do not pretend the benchmark is complete from read-only projection reports.

## Approved Benchmark Shape

If the user approves, keep the scope this narrow:

| item | value |
| --- | --- |
| stage | formatting only |
| provider | OpenRouter only |
| target concurrency | 2 |
| chapter scope | one bounded chapter after `ch050` |
| glossary | scan/approval already completed before benchmark translation continues |
| translation/refinement/QA | normal sequential routing unless separately approved |
| formatting | AI formatting remains required |
| validation | final-output guardrails required |

## Precheck Commands

Run before any benchmark implementation or benchmark execution:

```powershell
cd "D:\Fogust\Workspace\Novel\Deep Sea Embers"
$env:PYTHONIOENCODING='utf-8'
git status --short --untracked-files=no
git log -1 --oneline
python -m compileall novel_pipeline test_translation.py
python test_translation.py
python scripts\check_output_quality_guardrails.py
novel-pipeline --config ".system/config.yaml" preflight
```

Expected precheck state:

- compile/test/guardrails pass
- providers are ready
- `preflight` may remain `degraded` only because of the documented untracked queue
- no tracked diff before benchmark implementation starts

## Minimal Runtime Implementation Scope If Approved

If the benchmark is approved and no existing runtime harness is found, implement only:

- formatting-stage parallel execution
- OpenRouter formatting provider path only
- max worker count from `execution.stage_concurrency.formatting`
- active only when `execution.concurrency_enabled: true`
- bounded chapter/range only
- deterministic result ordering before ledger/final assembly
- stop-on-first-hard-failure behavior preserved

Do not implement:

- translation/refinement/QA parallelism
- cache skipping
- Pre-QA blocking
- provider routing changes
- global background job queue
- dashboard UX changes

## Temporary Config Rule

Do not edit `.system/config.yaml` permanently for the benchmark.

Use a temporary config copy, for example:

```powershell
Copy-Item ".system/config.yaml" ".system/config.v6_18_benchmark.yaml"
```

Then change only the temporary copy:

```yaml
execution:
  concurrency_enabled: true
  stage_concurrency:
    formatting: 2
```

After the benchmark, delete or archive the temporary config according to the benchmark report. `.system/config.yaml` must remain conservative unless the user separately approves a production routing/runtime change.

## Benchmark Command Shape

Exact production command depends on the approved post-`ch050` run ID and chapter. The command must remain bounded:

```powershell
novel-pipeline --config ".system/config.v6_18_benchmark.yaml" resume --run-id <approved-run-id> --until-chapter <approved-chapter> --manual-action-mode stop
```

If only one block must be recovered:

```powershell
novel-pipeline --config ".system/config.v6_18_benchmark.yaml" rerun-block --run-id <approved-run-id> --block-id <approved-block-id> --from-stage formatting
```

Do not run either command until:

- the user approves the exact scope
- source after `ch050` is confirmed
- scan/glossary approval for the benchmark chapter is complete
- the minimal formatting parallelism implementation is present and tested, if needed

## Stop Conditions

Stop immediately if any occur:

- provider failure
- command_too_long
- QA hard-fail
- manual prompt
- formatting validation failure
- output guardrail failure
- scope expands beyond the approved chapter
- any unapproved chapter is processed
- ledger state becomes ambiguous
- parallel formatting produces nondeterministic chapter assembly
- any tracked file changes outside the approved implementation/report scope

## Evidence Required In The Benchmark Report

The benchmark is not useful unless the report records:

- approved exact scope
- config file used
- baseline sequential timing source
- benchmark wall-clock timing
- per-block formatting durations
- provider/model used for formatting
- provider failures/retries
- QA failures/retries
- formatting validation result
- final-output guardrail result
- exact ledger records appended
- exact files changed
- rollback status proving `.system/config.yaml` remains conservative

## Success Criteria

V6.18A can move forward only if:

- benchmark is approved before execution
- runtime support is real, not just read-only projection
- output passes guardrails
- no QA or formatting regression occurs
- speed improvement is visible enough to justify further testing
- default runtime config remains conservative after the benchmark

## Next Safe Action

Ask for explicit approval. If approval is granted, first verify whether a minimal formatting-only runtime implementation exists. If it does not, implement that small runtime slice before attempting the benchmark.
