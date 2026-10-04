# TDU Lean Resume Order 02

## Scope

- Run: `TDU-LEAN-PILOT-20261004-ch001-010-v2`
- Recovery order: `TDU-LEAN-RESUME-20261004-02`
- Chapters: `ch006`, then `ch009-ch010`
- Source: corrected XSZJ raw pool; no source-parity change

## Result

- `ch006`: recovered from the earliest broken stage and promoted after normal QA, guardrails, and blocking Sentinel.
- `ch009`: stopped on the configured global Codex provider failure before a valid final output was produced.
- `ch010`: not reached.
- No force-accept, provider reroute, publication, commit, push, or control-document edit was performed by the worker.

## Verification

- Deterministic output guardrails: passed for TDU `ch001-ch010`.
- Final scoped Sentinel: `0 blocker / 0 major / 10 minor / 0 info`.
- Evidence: `sentinel_quality_TDU-LEAN-PILOT-20261004-ch001-010-v2-resume02-final_20261004_055622.md`.

## Blocker

The configured `codex-lb` route returned unusable output again at `ch009`. The worker stopped according to the global-provider stop rule. The stale/incomplete `ch009` and `ch010` outputs remain invalid and are not eligible for MoonRead.

## Next Safe Action

Restore and verify the configured provider authorization/health, then issue a new bounded continuation for `ch009-ch010`. Do not enable TDU in MoonRead until all ten chapters pass independent acceptance.
