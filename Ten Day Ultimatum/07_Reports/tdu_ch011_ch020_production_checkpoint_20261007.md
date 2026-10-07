# Ten Day Ultimatum `ch011-ch020` production checkpoint

Date: 2026-10-07
Scope: `ten-day-ultimatum`, exactly `ch011-ch020`
Run: `TDU-LEAN-PROD-20261007-ch011-020-r2`

## Outcome

The bounded Lean run is complete. All 10 requested chapters were promoted to `05_Output`; no chapter is quarantined, no current failed block remains, and no manual action is pending. No chapter outside the authorized range was translated or promoted.

Measured run metrics from `04_Work/_lean_runs/TDU-LEAN-PROD-20261007-ch011-020-r2/lean_run_report.json`:

- provider calls: 291
- recovered provider failures: 37
- total tokens: 1,197,471
- measured cost: `$1.8494568702`
- promoted chapters: 10/10
- quarantined chapters: 0

The TDU QA route is `openrouter_qa` with reasoning disabled and a 12,000-token ceiling. The partial-output guard now rejects terminal `finish_reason` values such as `length` and `content_filter` before an unsafe artifact can be accepted.

## Repairs applied during the run

- `ch012`: corrected the source-backed `ตีหนึ่ง`/`บ่ายโมง` time contradiction with a chapter-scoped repair rule.
- `ch013`: replaced copied CJK puzzle glyphs (`右`, `口`) with Thai readings while retaining the puzzle meaning.
- `ch020`: completed configured QA adjudication with source and Thai evidence; the accepted fallback result is recorded in the chapter ledger.
- Added regression coverage for TDU repair scoping/idempotence and provider partial-output finish reasons. The routing regression also accepts the existing `openrouter` QA provider used by another registered novel.

## Quality evidence

- TDU output guardrails: passed for `ch011-ch020`.
- Independent blocking Sentinel: `0/0/0/0`; report: `07_Reports/sentinel_quality_tdu-lean-final-independent-20261007_20261007_163131.md`.
- Required spot-check: `ch011`, `ch012`, `ch013`, `ch018`, `ch020`. Each sample was checked for title, opening, middle, ending, paragraph/dialogue layout, and obvious omission/truncation. CJK leakage was `0` and no provider/meta markers were present.
- Full regression suite: `Deep Sea Embers/test_translation.py` passed with exit code `0` under UTF-8 console output.
- Workspace doctor: `fail=0`, `unverified=0`; the existing portability warning remains unchanged.

## MoonRead publication

Command (from `MoonRead/`):

```powershell
$env:SENTINEL_NOVEL = "ten-day-ultimatum"
$env:SENTINEL_CHAPTERS = "ch011-ch020"
npm.cmd run publish:verify
```

Measured result:

- generated library: 6 books, 689 available chapters, 0 missing, 0 rejected
- TDU manifest: exact target range `ch001-ch020`, 20/20 available
- generated-content Sentinel: `0/0/0/0`; report: `07_Reports/sentinel_quality_moonread-generated_20261007_163248.md`
- `lint`, `build`, and `smoke`: passed
- generated TDU chapters match verified `05_Output` files: 10/10
- reader smoke covered TDU desktop/mobile chapter and navigation evidence; no console errors or horizontal overflow were reported

## Next action

Commit and push this verified change set. After push, check CI by the exact commit SHA, confirm the remote `main` head, rerun Yuehua doctor, and verify the MoonRead deployment surface. Keep future work bounded to a newly authorized range.
