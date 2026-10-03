# TDU Lean Pilot v2 Blocked Checkpoint

## Scope

- Run: `TDU-LEAN-PILOT-20261004-ch001-010-v2`
- Novel: Ten Day Ultimatum (`ten-day-ultimatum`)
- Source: corrected XSZJ raw pool, manifest `1385`, missing `0`, invalid source files `0`
- Requested range: `ch001-ch010`
- Publication: not run

## Verified State

- Promoted by this run: `ch001`, `ch002`, `ch003`, `ch005`, `ch006`, `ch007`, `ch008`
- Quarantined: `ch004`
- Not completed by this run: `ch009`, `ch010`
- Existing `05_Output/ch004`, `ch009`, and `ch010` files predate v2 and belong to the invalidated incomplete-raw run. They are not accepted evidence and must not be published or reused.
- The v2 staged chapters passed their per-chapter deterministic checks and blocking Sentinel with `0/0/0/0`.

## Blocker

The run ended with status `blocked` during `ch009` literal translation after the configured OpenRouter routes failed and the Codex fallback returned a nonzero exit:

`codex_rmcp_client::oauth::refresh_transaction: OAuth tokens for server vercel cannot be refreshed; authorization required`

Run metrics at stop:

- Provider calls: `78`
- Provider failures: `13`
- Provider time: `3084.873s`
- Reported cost: `$0.2623013352`
- Tokens: `299326` total (`155391` prompt, `143935` completion)

## Decision

- Do not force-accept `ch004`.
- Do not use the invalidated pre-v2 files for `ch004`, `ch009`, or `ch010`.
- Do not generate or publish MoonRead from this partial run.
- Resume only after the provider authorization/fallback blocker is resolved, using the same corrected raw source and run scope. Recover `ch004` from its earliest broken semantic stage, then complete `ch009-ch010`, run final guardrails, blocking Sentinel, and spot-check before publication.

## Evidence

- `04_Work/_lean_runs/TDU-LEAN-PILOT-20261004-ch001-010-v2/lean_run_report.json`
- `04_Work/_lean_runs/TDU-LEAN-PILOT-20261004-ch001-010-v2/ch004/qa_checkpoint.json`
- `04_Work/_lean_runs/TDU-LEAN-PILOT-20261004-ch001-010-v2/trace/`
- `03_Raw/manifest.json`
