# V6.18B Literal Translation Cache Skip

Date: 2026-06-16

Scope: first runtime cache-skip implementation for V6.18B.

## What Changed

- Added a disabled-by-default artifact cache skip path for the `translating` stage only.
- Runtime skip requires all of these conditions:
  - `execution.artifact_cache.mode: enabled`
  - `translating` is listed in `execution.artifact_cache.stages`
  - literal artifact exists and reconstructs into a valid `LiteralDraft`
  - artifact source text matches the current block source text
  - a previous completed translating ledger record exists for the same block with the same new literal input hash and matching output hash
- Cache hits append a current-run `translating/completed` ledger record with `provider: cache` and metadata identifying the source run/provider.
- Default production config remains `report_only`, so normal production runs do not skip provider calls silently.

## Hash Scope

The new literal translation input hash includes:

- cache version
- block/chapter ID
- source language
- source block text
- rendered literal prompt hash
- formatted glossary subset
- research context hash
- primary provider/model
- fallback route list

Old source-text-only hashes are intentionally not enough to trigger a runtime cache hit.

## Verification

- `python -m compileall novel_pipeline scripts test_translation.py`: passed
- `$env:PYTHONIOENCODING='utf-8'; python test_translation.py`: passed
- `git diff --check`: passed

## Remaining V6.18B Work

- Benchmark cache-enabled behavior on a small approved non-production run before using it operationally.
- Keep refinement, QA, and formatting cache skip disabled until their hash scopes are proven complete.
- Keep AI formatting primary; this cache work does not change formatting behavior.
