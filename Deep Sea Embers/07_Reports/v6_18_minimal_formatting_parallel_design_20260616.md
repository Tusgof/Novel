# V6.18 Minimal Formatting Parallel Runtime Design - 2026-06-16

Purpose: define the smallest runtime implementation slice needed before a real `formatting/openrouter concurrency=2` benchmark can run.

No provider calls were made. No pipeline commands were run. No ledger, glossary notes, source files, output files, MoonRead files, provider config, or runtime artifacts were modified.

## Current Code Shape

Relevant files inspected:

- `novel_pipeline/types.py`
- `novel_pipeline/pipeline.py`
- `novel_pipeline/reports.py`
- `.system/config.yaml`

Current findings:

- `ExecutionPolicy` parses `concurrency_enabled` and `stage_concurrency`.
- `.system/config.yaml` defines `stage_concurrency.formatting: 2`, but keeps `concurrency_enabled: false`.
- `reports.py` can produce read-only projection/benchmark reports.
- `pipeline.py` currently processes each block sequentially through:
  - translate
  - refine
  - QA
  - format
  - completed
- `_process_block()` owns all per-block stages and writes/commits formatting.
- `_resume_chapter()` and batch processing append formatted block text in block order as blocks finish.

Therefore, enabling YAML alone cannot produce a true parallel formatting benchmark.

## Minimal Safe Design

Implement only a formatting-stage helper that runs after translation/refinement/QA are already complete for multiple blocks.

Do not parallelize full `_process_block()`.

Why:

- Full block parallelism would also parallelize translation/refinement/QA.
- QA hard-fail/manual prompts are not safe to run concurrently.
- Chapter assembly order must stay deterministic.
- Ledger append order should remain auditable.

## Proposed Runtime Slice

Add a small helper, conceptually:

```python
def _format_ready_blocks_parallel(
    *,
    ctx: PipelineContext,
    blocks: list[TextBlock],
    refined_by_block: dict[str, RefinedDraft],
    force: bool = False,
) -> dict[str, str]:
    ...
```

Behavior:

- Only runs when:
  - `config.execution.concurrency_enabled` is true
  - `config.execution.effective_stage_limit("formatting") > 1`
  - all selected blocks already have completed QA or force-accepted/skipped QA
  - all selected blocks have readable refined artifacts
- Uses max workers from `effective_stage_limit("formatting")`.
- Calls existing `_format_block_with_hybrid_provider()` per block.
- Runs existing `validate_formatted_text()` per block.
- Writes `formatted.json` per block.
- Commits `formatting completed` per block with the actual formatter provider and metadata.
- Commits `completed` per block only after formatting validation passes.
- Returns a dict keyed by `block_id`.
- Caller assembles chapter output by original block order, not completion order.

## Where To Hook It

Smallest hook point:

- `_resume_chapter()` only.

Why `_resume_chapter()` first:

- V6.18 benchmark command packet uses bounded `resume`.
- It avoids changing initial full `run --range` batch behavior.
- It keeps the blast radius smaller than modifying every path that calls `_process_block()`.

Eligible block pattern:

- block next pending stage is `formatting`, or
- force-from-stage is `formatting`, if later wired through a bounded command

Non-eligible blocks should still use existing `_process_block()` sequentially.

## Implementation Guardrails

Keep these unchanged:

- translate/refine/QA sequential behavior
- manual-action-mode stop behavior
- QA hard-fail handling
- final output assembly from `formatted_blocks` in source block order
- default `.system/config.yaml` conservative values
- existing `_format_block_with_hybrid_provider()` validation and local fallback behavior

Add tests before/with implementation:

1. `ExecutionPolicy.effective_stage_limit("formatting")` still returns `1` unless `concurrency_enabled: true`.
2. Parallel formatting helper refuses blocks without completed QA.
3. Parallel formatting helper preserves output assembly order even if individual formatting calls finish out of order.
4. Formatting validation failure stops the helper and records a failed formatting stage.
5. When `concurrency_enabled: false`, `_resume_chapter()` still uses the existing sequential path.

## Benchmark Preconditions

Before benchmark execution:

- user explicitly approves the exact V6.18 scope
- implementation tests pass
- `.system/config.yaml` remains unchanged
- benchmark uses temporary config only
- benchmark target is one bounded chapter after `ch050`
- scan/glossary approval for that chapter is complete

## Non-Goals

Do not implement:

- translation parallelism
- refinement parallelism
- QA parallelism
- global task queue
- dashboard progress streaming
- cache skip enablement
- Pre-QA blocking
- provider routing changes

## Risk Register

| risk | mitigation |
| --- | --- |
| ledger records interleave unexpectedly | keep metadata explicit and assemble by block order |
| provider rate/concurrency failure | stop on first provider failure; benchmark only concurrency=2 |
| formatting output order changes | return dict by block ID and assemble using original `blocks` order |
| hidden QA/manual prompt in parallel path | only accept blocks whose QA is already complete |
| default config accidentally left parallel | use temporary config and verify `.system/config.yaml` remains conservative |

## Recommendation

If the user approves V6.18 implementation, implement only `_resume_chapter()` formatting-stage parallelism first, guarded by config and tests. Then run the single approved benchmark.
