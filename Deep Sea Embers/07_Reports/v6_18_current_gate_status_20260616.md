# V6.18 Current Gate Status - 2026-06-16

Purpose: record the current V6.18 decision state after V6.13 cleanup progress, without running benchmarks or changing runtime configuration.

No provider calls were made. No pipeline commands were run. No ledger, glossary notes, source files, output files, MoonRead files, provider config, or runtime artifacts were modified.

## Current State

Tracked repository state:

- latest pushed commit: `0d3187d` (`Commit durable provider decision reports`)
- durable provider/glossary evidence reports are now tracked
- remaining visible queue:
  - 46 untracked glossary notes
  - 14 untracked intermediate/probe reports

Root docs:

- canonical docs remain at `D:\Fogust\Workspace\Novel`
- `PROJECT_BRAIN.md`, `IMPLEMENT_PLAN.md`, and `DOC_RECOVERY.md` describe the current queue and V6.18 gate
- root docs are outside the nested git repo and protected by the local snapshot listed in `DOC_RECOVERY.md`

## V6.18 Gate

V6.18 is still not approved for runtime execution.

The only currently approved-by-plan next speed experiment shape is:

```text
formatting/openrouter concurrency=2 on one bounded chapter after ch050
```

However, this experiment must not run until the user explicitly approves:

```text
Approve V6.18 formatting/openrouter concurrency=2 benchmark on one bounded chapter after ch050.
```

## Why The Gate Remains

V6.18 is about speed, but speed changes can reduce translation quality if they create:

- provider contention
- hidden retry/fallback behavior
- formatting drift
- harder-to-debug block order
- stale artifact reuse
- missed QA/manual prompts

The current safe posture is therefore:

- runtime concurrency: disabled
- artifact cache skip: disabled / report-only
- Pre-QA blocking: disabled / report-only

## Safe Work Until Approval

Safe:

- read-only planning reports
- documentation sync
- report-only cleanup proposals
- verifying current output quality without provider calls
- preparing exact commands for the benchmark without executing them

Not safe without explicit approval:

- running the V6.18 benchmark
- enabling concurrency
- enabling cache skip
- enabling Pre-QA blocking
- starting a new production translation batch
- changing provider routing
- archiving/deleting the remaining queue

## Remaining Cleanup Decisions

Glossary queue:

- decide whether `真实的太阳神` should become an alias of canonical `实太阳神`
- do not commit/delete the 46 untracked glossary notes until this decision is made

Report queue:

- 5 durable evidence reports have already been committed
- 14 intermediate/probe reports remain visible
- archive them only after explicit cleanup approval, or leave them visible

## Next Practical Choices

1. Approve the V6.18 benchmark exact scope and run one bounded formatting/concurrency test.
2. Approve the glossary alias cleanup for `真实的太阳神` -> alias of `实太阳神`.
3. Approve archiving the 14 intermediate/probe reports under `07_Reports/archive/20260609_openrouter_qa_formatting/`.
4. Keep all risky work paused and continue with read-only planning only.
