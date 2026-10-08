# Ten Day Ultimatum `ch021-ch025` production checkpoint

Date: 2026-10-08
Novel: Ten Day Ultimatum (`ten-day-ultimatum`)
Range: `ch021-ch025` only
Translator label: `[Lean]`
Run: `TDU-LEAN-PROD-20261008-ch021-025`

## Translation run

- Lean run status: `complete`.
- Chapters promoted: `5/5`; blocks: `4, 4, 4, 5, 5` for `ch021` through `ch025`.
- Current failed blocks: `0`; quarantined chapters: `0`; unresolved manual action: `0`.
- The first pass quarantined `ch021` and `ch025` when QA adjudication evidence was incomplete. A bounded resume reused valid literal/refinement checkpoints, reran the affected QA path, and promoted both chapters without force-accept.
- Provider recovery is recorded in the run trace: `10` recovered failures (`6` content-filter, `1` nonzero-exit, `1` truncated-output, `2` timeout). All recovered through the configured fallback chain; no global provider failure occurred.
- Metrics: `53` provider calls, `183,941` total tokens, `2270.02s` provider time, measured cost `$0.380600434001`.
- Run report: `Ten Day Ultimatum/04_Work/_lean_runs/TDU-LEAN-PROD-20261008-ch021-025/lean_run_report.json`.

## Quality acceptance

- Deterministic output guardrails: passed for `ch021-ch025`.
- Per-chapter runtime Sentinel: blocker/major/minor/info `0/0/0/0` for all five chapters.
- Independent Sentinel: blocker/major/minor/info `0/0/6/0`, `safe_to_publish: yes`; report: `07_Reports/sentinel_quality_tdu-lean-final-independent-20261008_20261008_091715.md`.
- The six minor findings are source-backed English names/site/game references: `Xiaoshuozhijia`, `xszj.org`, `League of Legends`, and `Fatal Fury`. No blocker or major finding remains.
- Spot-check covered every chapter in the five-chapter range: title, opening, middle, ending, paragraph layout, dialogue/thought formatting, CJK leakage, and provider/meta markers. All five had `0` CJK characters and no metadata markers.
- Normalized LF parity between verified `05_Output` and generated TDU reader files: `5/5` equal.

## MoonRead publication gate

- Registry now targets TDU `last_chapter: 25` and `lean_retranslated_through: 25`.
- `MoonRead` `npm.cmd run publish:verify` with `SENTINEL_NOVEL=ten-day-ultimatum` and `SENTINEL_CHAPTERS=ch021-ch025`: passed.
- Generated reader: `6` books, `694` available chapters, `0` missing, `0` rejected.
- TDU manifest: target `ch001-ch025`, available `25/25`; chapters `ch021-ch025` are labeled `[Lean]`.
- Generated-content Sentinel: blocker/major/minor/info `0/0/0/0`.
- MoonRead lint, production build, smoke, and desktop/mobile reader checks passed. TDU `ch001` and `ch025` rendered with matching titles and `[Lean]` translator labels, with no horizontal overflow.

## Verification and landing

- Yuehua doctor before landing: `fail=0`, `unverified=0`; existing portability warning covers `397` files with absolute paths.
- TDU preflight: providers ready; only the pre-existing dirty-worktree warning remains.
- `python -m compileall novel_pipeline scripts/sentinel_quality_report.py scripts/check_output_quality_guardrails.py`: passed.
- `python -m unittest -v test_workspace_routing.py test_xszj_adapter.py`: `23` tests passed.
- Unrelated DSE/IRS generated files and reports were left unstaged as dirty WIP. Only TDU artifacts, TDU reader metadata, quality evidence, registry, checkpoint, and control-document updates belong to this change.
- Commit/push and post-push live alias evidence are recorded in the follow-up landing update.
