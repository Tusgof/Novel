# Ten Day Ultimatum ch001-ch010 Production Checkpoint

- Date: 2026-10-04 (Asia/Bangkok)
- Novel: `ten-day-ultimatum`
- Requested range: `ch001-ch010`
- Raw gate: complete through `ch1385`; `03_Raw/manifest.json` contains 1,385 entries and `ch1385/source.json` is present (1,246 bytes).
- Publication: no deployment or publish command was run for this task. During final checks, a local `MoonRead/content/generated/books/ten-day-ultimatum/` export appeared, with all ten chapters marked available; its manifest records `generatedAt: 2026-10-03T20:11:24.222Z` and `sourceRoot: ../Ten Day Ultimatum/05_Output`. I did not run the generator and left the newly created, untracked files untouched. No deployment evidence was found.

## Runs

1. `tdu-ch001-ch010-20261004`
   - Result: `partial`; 7 promoted, 3 quarantined.
   - Quarantines: `ch002` omission, `ch007` corrupted spelling/title consistency, `ch008` semantic mistranslation.
   - Provider calls/failures: 58/7; measured cost: `$0.17415496436`.
2. `tdu-ch002-ch007-ch008-recovery-20261004`
   - Result: `partial`; `ch002` and `ch008` promoted; `ch007` quarantined again on title consistency adjudication.
   - Provider calls/failures: 16/2; measured cost: `$0.028314703`.
3. `tdu-ch007-recovery2-20261004`
   - Result: `complete`; `ch007` promoted.
   - Provider calls/failures: 6/1; measured cost: `$0.009941801`.

Final local product state: all ten chapters `ch001-ch010` are present in `05_Output`, with no quarantined chapter remaining. Harvested glossary candidates remain proposed; none were promoted into the production glossary.

## Verification

- Preflight: the initial check rejected `status: reviewed`; when preflight later passed, the profile had the accepted `active` status and the missing `last_reviewed_at` was set to `2026-10-04`. Only the pre-existing dirty-worktree warning remains.
- Title sidecars: all ten `04_Work/chNNN/title.json` files created using the explicit TDU config; report: `06_Logs/title_translation_last.json`.
- Deterministic guardrails: `python scripts/check_output_quality_guardrails.py --config "Ten Day Ultimatum/.system/config.yaml" --chapters ch001-ch010` -> `passed` (also passed after the local reader export appeared).
- Final Sentinel: production scope `tdu-ch001-ch010-final` and observed reader scope `tdu-ch001-ch010-reader-final-observed` both returned `0/0/0/0` (blocker/major/minor/info). Reports: `07_Reports/sentinel_quality_tdu-ch001-ch010-final_20261003_200924.md` and `07_Reports/sentinel_quality_tdu-ch001-ch010-reader-final-observed_20261003_201515.md`.
- Spot-checks: `ch001`, `ch003`, `ch006`, `ch007`, `ch009`, and `ch010`; titles, opening/middle/ending passages, paragraph density, dialogue, and recurring names were inspected. Each sampled chapter has 26 paragraphs. The source OCR placeholder in `ch010` (`??`) remains visible in the source-derived question line; QA accepted the contextual calculation elsewhere in that chapter.

## Next safe action

Keep these ten chapters local in `05_Output`. Do not deploy or modify the newly generated MoonRead files until a separate publication order is issued.
