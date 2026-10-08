# Infinite Regressor Stories ch021-ch030 production checkpoint

Date: 2026-10-08
Novel: Infinite Regressor Stories (infinite-regressor-stories)
Range: ch021-ch030 only
Translator label: [Lean]
Runs: IRS-LEAN-PROD-20261008-ch021-025 and IRS-LEAN-PROD-20261008-ch026-030

## Translation runs

- Both Lean production runs are complete. Each run promoted 5/5 chapters; current failed blocks, quarantined chapters, and unresolved manual actions are all zero.
- IRS-LEAN-PROD-20261008-ch021-025 promoted ch021-ch025 with 15 blocks (3 per chapter), 54 provider calls, 5 recovered provider failures, and 3166.499 provider seconds. Cost was not measured because the provider reported no cost metadata.
- IRS-LEAN-PROD-20261008-ch026-030 promoted ch026-ch030 with 16 blocks (4, 3, 3, 3, 3), 62 provider calls, 9 recovered provider failures, and 5451.986 provider seconds. Cost was not measured because the provider reported no cost metadata.
- The run reports show no experiment glossary promotions; harvested terms remained proposed. Run reports:
  - Infinite Regressor Stories/04_Work/_lean_runs/IRS-LEAN-PROD-20261008-ch021-025/lean_run_report.json
  - Infinite Regressor Stories/04_Work/_lean_runs/IRS-LEAN-PROD-20261008-ch026-030/lean_run_report.json

## Quality acceptance

- Deterministic output guardrails passed for ch021-ch030.
- Runtime Sentinel passed for every promoted chapter with blocker/major/minor/info 0/0/0/0.
- Independent blocking Sentinel passed with blocker/major/minor/info 0/0/0/0 and safe_to_publish yes:
  07_Reports/sentinel_quality_IRS-LEAN-PROD-20261008-ch021-030-final-verify_20261008_113504.md
- The independent post-publish advisory scan passed with blocker/major/minor/info 0/0/80/0. The 80 minor findings are source-backed English names, titles, usernames, quotations, or proper nouns and do not block publication:
  07_Reports/sentinel_quality_IRS-LEAN-PROD-20261008-ch021-030-inspector-postpublish_20261008_112206.md
- An earlier pre-publish scan saw one stale generated-content glossary blocker for Puppeteer in ch027. Regenerating MoonRead from the final output removed that stale blocker; the post-publish scan above is the accepted reader-surface result. The earlier evidence is retained at 07_Reports/sentinel_quality_IRS-LEAN-PROD-20261008-ch021-030-inspector_20261008_111451.md.
- Inspector spot-check covered ch021, ch023, ch028, ch029, and ch030. Source-to-output length ratios were approximately 1.01, 0.99, 0.93, 0.99, and 1.00; maximum paragraph sizes were 591, 584, 590, 599, and 381 characters. Titles, opening/middle/ending passages, dialogue/thought spacing, and chapter endings were inspected. No Han/CJK body text, provider metadata, or runaway repeated characters were found.

## Chapter-local repairs

- Repair cycle 3 is closed as complete in the run evidence. ch028 received spacing-only paragraph reflow and bounded density splits with non-whitespace content preserved.
- ch029's truncated refinement checkpoint was invalidated and rerun from the complete literal checkpoint. Follow-up repairs removed a duplicate chapter header, restored the source-backed ending, and corrected the documented dialogue particles and address forms. No omission was hidden by patching the final Markdown.
- Repair evidence, including pre-repair backups and checkpoint hashes, remains under Infinite Regressor Stories/04_Work/_lean_runs/IRS-LEAN-PROD-20261008-ch026-030/repair_evidence/. The prevention mechanism is earliest-stage checkpoint invalidation for truncation and local formatter reflow for Markdown-only density defects.

## MoonRead publication gate

- Registry reader state now records lean_retranslated_through: 30 for Infinite Regressor Stories.
- MoonRead publish verification was run with SENTINEL_NOVEL=infinite-regressor-stories and SENTINEL_CHAPTERS=ch021-ch030.
- Generated reader summary: 6 books, 694 available chapters, 0 missing, and 0 rejected.
- The Infinite Regressor Stories manifest covers ch001-ch070 with 70/70 available. ch021-ch030 are all labeled [Lean].
- Generated-content Sentinel passed with blocker/major/minor/info 0/0/0/0:
  07_Reports/sentinel_quality_moonread-generated_20261008_114021.md
- MoonRead lint, production build, smoke, desktop/mobile reader checks, title matching, translator labels, TOC row counts, and no-horizontal-overflow checks passed. The smoke evidence included IRS ch030 on desktop and mobile.
- The generated IRS files for ch021-ch030 match the verified 05_Output Markdown after newline normalization (10/10).

## Verification and landing

- Yuehua doctor before landing: fail=0, unverified=0; the existing portability warning remains for absolute paths in 401 document/data/test/example files.
- IRS preflight found every configured provider ready. Its only warning was the pre-existing dirty working tree containing unrelated WIP.
- The exact change set stages only the IRS registry update, IRS generated reader chapters/manifest, IRS quality evidence, this checkpoint, and control-document updates. Existing DSE and other-novel WIP remains unstaged.
- Measured landing: commit `a4d18a1dce082f650d0a4dc4f98b8b46c08bedab` is pushed to `main`; GitHub `tests` run `37775243403` completed successfully on that exact commit.
- Measured live reader: `https://novel-pink-nu.vercel.app/books/infinite-regressor-stories/read/ch021`, `/read/ch030`, and `/books/infinite-regressor-stories/chapters` returned HTTP 200. Both chapter pages contained Thai title/body text and `[Lean]`; the chapter list contained both chapter IDs and `[Lean]`.
