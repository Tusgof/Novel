# Immortality System Libra - Pilot Gate: Term Provider Stop

Date: 2026-08-28
Status: stopped before in-sample completion
Scope: isolated in-sample glossary approval for immortality-libra-v1-insample

## Verified State

- Novel543 raw source is complete through ch2570 (2570/2570 usable chapters).
- The locked 20-chapter sample still has source parity 0 mismatches.
- In-sample scan has 73 candidates; out-of-sample scan has 66 candidates.
- Seven in-sample chapters are complete in the isolated experiment run: ch1307, ch1765,
  ch2439, ch2307, ch741, ch1424, and ch1631 (29 blocks total).
- Their experiment outputs exist and no production 05_Output, production glossary, or MoonRead
  content was changed.
- ch376 has been fetched and scanned with 26 pending glossary terms. ch338 and ch984 remain at
  the same pre-translation glossary boundary. Out-of-sample translation has not started.

## Stop Evidence

The run stopped while approving the term 錢雅 for ch376:

    No safe Thai glossary options for 錢雅 after configured provider fallbacks.
    Provider claude returned unusable output (nonzero_exit).
    Failed to authenticate: OAuth session expired and could not be refreshed

The command exited nonzero. No glossary approval was committed for ch376, no block was
translated for that chapter, and no force-accept or manually invented translation was used.

## Root Cause

1. The term-suggestion chain did not produce three safe Thai options for 錢雅.
2. The final configured fallback was the local Claude CLI, whose OAuth session had expired and
   could not be refreshed. The chain therefore failed closed at the glossary gate.
3. This is a provider-readiness incident, not evidence that the source term should be skipped or
   that a guessed transliteration is acceptable.

## Prevention

- Keep glossary approval fail-closed when a term has fewer than three parseable Thai options.
- Run the exact term-suggestion health probe and verify fallback credentials before resuming the
  pilot; do not treat an expired fallback authentication error as a successful route.
- Resume the existing run ID after provider readiness is restored so the completed 29 blocks remain
  cached and the failed chapter starts at its glossary boundary.
- Keep the final title/glossary consistency guard enabled. It previously caught a stale ch1424
  title sidecar using หลิวอีดาว; the sidecar was regenerated through the title provider pipeline
  after 劉一刀 -> หลิวอี้เตา was approved and now passes the required-term check.

## Next Safe Action

Do not start OOS or production translation. Restore a usable term-suggestion route, rerun the exact
health probe, then resume:

    novel-pipeline --config .system/config.yaml resume --run-id immortality-libra-v1-insample --manual-action-mode stop

The next glossary boundary is ch376 / 錢雅; after that, complete ch338 and ch984, run the
in-sample guardrails and Sentinel, and only then begin the untouched OOS sample.

## Artifacts

- 04_Work/_experiments/libra_pilot_immortality_system_v1/06_Logs/run_ledger.jsonl
- 04_Work/_experiments/libra_pilot_immortality_system_v1/04_Work/ch376/glossary_scan.json
- 04_Work/_experiments/libra_pilot_immortality_system_v1/04_Work/ch1424/title.json
- 04_Work/_experiments/libra_pilot_immortality_system_v1/05_Output/ch1424/ch1424.md
- 07_Reports/immortality_system_libra_pilot_title_provider_stop_20260828.md
