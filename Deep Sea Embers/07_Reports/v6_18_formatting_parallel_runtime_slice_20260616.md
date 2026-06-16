# V6.18 Formatting Parallel Runtime Slice - 2026-06-16

Scope: implement the smallest runtime slice needed before a real V6.18 formatting concurrency benchmark can run.

No provider calls were made. No pipeline run/resume/rerun commands were executed against production runs. No ledger, glossary, source, output, provider config, or runtime artifact was modified.

## Implemented

- Added a guarded formatting-only parallel helper in `novel_pipeline/pipeline.py`.
- Hooked the helper only into `_resume_chapter()`.
- The helper runs only when `execution.concurrency_enabled` is true and `execution.stage_concurrency.formatting` is greater than 1.
- Only consecutive blocks whose next pending stage is `formatting` are eligible.
- Each eligible block must already have QA committed as completed, force-accepted, or skipped.
- Provider formatting calls may run in parallel, but formatted artifacts and ledger records are written on the main thread in original block order.
- Default `.system/config.yaml` remains conservative; runtime concurrency is still disabled.

## Tests Added

- `_resume_chapter()` uses the guarded parallel path only for consecutive formatting-ready blocks.
- `_format_ready_blocks_parallel()` commits formatting/completed records in block order.
- Existing execution policy tests still prove configured stage concurrency is inert unless `concurrency_enabled` is explicitly true.

## Validation

- `python -m compileall novel_pipeline test_translation.py` passed.
- `PYTHONIOENCODING=utf-8 python test_translation.py` passed.

## Remaining V6.18 Gate

V6.18 is still not complete. The acceptance gate still requires a real approved benchmark proving speed improvement without quality regression.

Current blocker remains benchmark target selection:

- The original benchmark scope requires one bounded chapter after `ch050`.
- The current Deep Sea Embers workspace has source/output only through `ch050`.
- The user must choose whether to fetch/prepare a new chapter after `ch050` or approve using an already-published chapter as a non-production benchmark fixture.
