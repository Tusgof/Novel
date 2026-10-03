# Lean Retranslation Publication

## Scope

- DSE, HGD, IRS, OHKS: replace chapters 1-20 with verified Lean production output.
- Re:Zero: replace chapters 1-2 only. Chapters 3-20 are not authorized by this order.
- Reader labels: `[Lean]` for verified replacement chapters, `[Pipe]` for retained legacy chapters.
- Preserve the existing reader ranges outside the replacement scope.
- Inspector owns acceptance/publication/git. Workers own isolated translation and routine recovery.

## Checkpoint

Publication is pending. This file is not a completion claim.

| Novel | Production evidence | Inspector checks | Remaining |
| --- | --- | --- | --- |
| DSE | Four complete runs cover ch001-ch020 | Output guardrails passed; Sentinel 0/0/1/0; sampled ch001,ch005,ch010,ch015,ch020 | Reader regeneration and publication |
| HGD | Four complete runs cover ch001-ch020, all promoted with QA pass | Output guardrails passed; Sentinel 0/0/18/0; sampled ch001,ch005,ch010,ch017,ch020 | Narrow ordinary English/UI repair, then final acceptance |
| IRS | `LEAN-RETRANSLATE-20261003-IRS-b01` complete ch001-ch005 | Final acceptance pending remaining chapters | ch006-ch010 recovery; separate ch011-ch020 worker |
| OHKS | Complete production runs cover ch001-ch020 | Output guardrails passed; Sentinel 0/0/80/0 | Source-backed UI/stat English review, then reader acceptance |
| R0 | `LEAN-RETRANSLATE-20261003-R0` complete ch001-ch002 | Output guardrails passed; Sentinel 0/0/29/0; both chapters sampled | Narrow ch002 prose English repair, then final acceptance |

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
- New reader content has not been committed or pushed at this checkpoint.
- Reader preview generation: 5 books, 669 available, 0 missing, 0 rejected; IRS still labels only ch001-ch005 as Lean pending final acceptance.
- Updated reader smoke: passed 28 reader samples and 10 TOC layouts across 1440px/390px, no unexpected console errors or horizontal overflow. Renderer now avoids duplicate chapter H1 and handles triple/quadruple emphasis plus ASCII separators. This preview is not a publication claim.
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

Require all 82 replacements to have source-backed QA, no current quarantine/manual gate, deterministic guardrail pass, blocking Sentinel pass, and Inspector spot-check acceptance. Then regenerate reader content, verify labels and Markdown parity, run scoped `publish:verify`, lint/build/smoke, inspect desktop/mobile output, commit/push, verify remote HEAD and live reader before claiming ready.
