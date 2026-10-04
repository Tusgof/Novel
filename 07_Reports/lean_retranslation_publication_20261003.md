# Lean Retranslation Publication

## Scope

- DSE, HGD, IRS, OHKS: replace chapters 1-20 with verified Lean production output.
- Re:Zero: replace chapters 1-2 only. Chapters 3-20 are not authorized by this order.
- Reader labels: `[Lean]` for verified replacement chapters, `[Pipe]` for retained legacy chapters.
- Preserve the existing reader ranges outside the replacement scope.
- Inspector owns acceptance/publication/git. Workers own isolated translation and routine recovery.

## Checkpoint

The five-novel replacement publication gate passed on 2026-10-04 and was pushed/live-verified at commit `14020e6120d61483971b68197ce5b8fa6cbf50b5`. TDU setup is valid but its ten-chapter translation remains blocked and is not enabled in MoonRead. This file is a partial-scope completion record, not a claim that TDU is complete.

| Novel | Production evidence | Inspector checks | Remaining |
| --- | --- | --- | --- |
| DSE | Lean replacement ch001-ch020 accepted | Output guardrails passed; MoonRead Sentinel 0/0/0/0; desktop/mobile spot-check passed | Complete: reader regenerated and publication artifacts ready |
| HGD | Lean replacement ch001-ch020 accepted | Output guardrails passed; MoonRead Sentinel 0/0/0/0; desktop/mobile spot-check passed | Complete: reader regenerated and publication artifacts ready |
| IRS | Lean replacement ch001-ch020 accepted | Output guardrails passed; MoonRead Sentinel 0/0/0/0; desktop/mobile spot-check passed | Complete: reader regenerated and publication artifacts ready |
| OHKS | Lean replacement ch001-ch020 accepted | Output guardrails passed; MoonRead Sentinel 0/0/0/0; desktop/mobile spot-check passed | Complete: reader regenerated and publication artifacts ready |
| R0 | Lean replacement ch001-ch002 accepted | Output guardrails passed; MoonRead Sentinel 0/0/0/0; desktop/mobile spot-check passed | Complete: reader regenerated and publication artifacts ready |

Counts are blocker/major/minor/info. Advisory English findings require source-backed classification, not automatic removal of brands, usernames, or author references.

## Ownership

- `wK:pB`: IRS ch006-ch010 and its quarantined recoveries only; explicitly excluded ch011-ch020.
- `wK:pA`: IRS ch011-ch015, including their recoveries; ownership amendment excludes ch016-ch020. Assign the latter only after an acknowledged handoff.
- `wK:p9`: OHKS targeted reader QA, ch001-ch020; no full re-refinement or routing change.
- `wK:pC`: `READER-ENGLISH-HGD-R0-20261003`, source-backed HGD ch001-ch020 and R0 ch001-ch002 ordinary English repairs; no OHKS ownership.
- Original `wK:pC` OHKS repair assignment failed before ACK due session bridge HTTP 503; superseded by `wK:p9`, no active overlapping owner.
- R0 ch003-ch020 order was canceled as out of scope; not a publication dependency.

## Verification

- `python -X utf8 -m unittest -q test_workspace_routing.py`: 14 tests passed after cleaner-preservation and chapter-scoped Sentinel evidence regressions.
- `python -X utf8 -m compileall -q novel_pipeline`: passed.
- From `Deep Sea Embers`, `python -X utf8 test_translation.py`: all tests passed.
- From `MoonRead`, `npm.cmd run lint`: passed.
- Independent output-only Sentinel uses `NOVEL_SENTINEL_STAGE_ONLY=1`; reader-inclusive gates will run after regeneration.
- Reader generation: 5 books, 669 available, 0 missing, 0 rejected. Replacement labels are `[Lean]` through the requested ranges and retained legacy chapters are `[Pipe]`.
- MoonRead scoped Sentinel: DSE/HGD/IRS/OHKS ch001-ch020 and R0 ch001-ch002 each report `0/0/0/0` at `07_Reports/sentinel_quality_moonread-lean-final-20261004_20261004_060429.md` through `060435.md`.
- `npm.cmd run lint`, `npm.cmd run build`, and `npm.cmd run smoke` passed. Smoke checked 1440px/390px reader pages, TOCs, labels, titles, emphasis, and no horizontal overflow; no unexpected console errors occurred.
- HGD ch001-ch020 source sequence check: passed, source chapter numbers 1-20 match local IDs.

## Incidents And Backlog

- Confirmed Layer 0 cleaner defect: IRS ch007 provider refinement trace contains all 12 slogan/comment bullet lines, but `_clean_refined_output()` dropped every `- ` line. It also truncated prose at the first ASCII `---` separator. The cleaner now preserves story list lines and scene tails; explicit Craft notes remain stripped. Regression tests pass, and workers must revalidate any recovered candidate rather than inherit a stale QA verdict.
- Confirmed evidence collision: per-chapter Sentinel calls reused one run scope and second-resolution filename, so ch009 overwrote the report referenced by ch006 in the same second. Production Sentinel scope now includes the chapter; regression verifies distinct ch001/ch002 paths and that ch001 evidence remains intact. Final Inspector scans use unique per-novel scopes and do not rely on overwritten historical files.
- IRS ch011 refinement ended at `ที่พัก` before a large source tail containing the OldManGoryeo/Sim Ah-ryeon reveal. Glossary coverage blocked it; Inspector confirmed broad truncation against raw source and directed earliest-broken-stage recovery, not tail patching.
- HGD advisories included actual untranslated game UI/prose, and R0 ch002 included `wonder`, `overwhelmed`, `desperately` in story prose. Advisory severity is not permission to ignore actual reader defects; these were assigned to narrow QA before acceptance.
- The canceled R0 ch003-ch005 worker left a subprocess running. Inspector independently checked exact PIDs after the repair worker reported it; it had just exited at 16:12:54 UTC. Its blocked report has `promoted_outputs=[]`, 51 provider calls, 6 failures and no reported cost. R0 ch003-ch008 output timestamps and reader diffs remain unchanged. Do not resume this out-of-scope run. Prevention: cancel a worker only with verification that its owned subprocess tree has exited; an agent cancellation alone is not process termination.
- Selected-vault OpenRouter helper copies for IRS/HGD differ from the root shim; the observed IRS trace has empty usage metadata. Keep cost claims as `not measured` and log helper convergence separately; no provider-routing/helper change is part of this publication order.

## Acceptance Evidence

- `07_Reports/sentinel_quality_lean-close-dse-output_20261003_152843.md`
- `07_Reports/sentinel_quality_lean-close-hgd-output_20261003_153553.md`
- `07_Reports/sentinel_quality_lean-close-ohks-output_20261003_152852.md`
- `07_Reports/sentinel_quality_lean-close-r0-output_20261003_152901.md`
- `Deep Sea Embers/07_Reports/checkpoint_dse-lean-rest-20261003-ch011-ch020.md`
- `Horror Game Developers/07_Reports/HGD-LEAN-CONTINUE-20261003-v3_checkpoint_20261003.md`
- `Re Zero Watching Him Die Again and Again/07_Reports/rezero_lean_continue_20261003_R0_v2_checkpoint.md`

## Publication Gate

For the five-novel replacement scope, all 82 replacements have source-backed QA, no current quarantine/manual gate, deterministic guardrail pass, blocking Sentinel pass, Inspector spot-check acceptance, regenerated reader content, correct labels, and passing lint/build/smoke. Commit/push and live deployment verification passed at `14020e6120d61483971b68197ce5b8fa6cbf50b5`; all five chapter-1 live URLs returned HTTP 200 and displayed `[Lean]`. TDU is excluded until all ten chapters pass its own gate.
