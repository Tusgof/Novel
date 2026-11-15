# Fusionpunk first forty — local reader acceptance

**Measured outcome:** accepted Gacha ch001-ch040 is generated into the local
MoonRead snapshot with forty explicit `[Code]` labels. This is ready for landing
review, **not** a deployed result. Investing and Gacha ch041+ are absent.

## Scope and preservation

- New library: seven books, 734 available chapters, zero missing/rejected.
- The new book contains exactly ch001-ch040. Each generated body matches accepted
  output after the generator's declared CRLF-to-LF normalization; none needed
  trailing-whitespace repair. This is content equality, not a false byte-equality
  claim between CRLF source output and LF generated text.
- **982/984** original baseline files remain byte-identical, including every old
  book manifest/chapter, legacy chapter copy and legacy root manifest. The only
  expected old files changed are aggregate `library.json` and `import-report.md`.
- No local-only TDU or extra primary DSE/HGD output was imported, and no source,
  translation checkpoint, glossary or ledger was edited by reader generation.

## Real-surface checks

- Scoped `publish:verify` passed generation, blocking Sentinel, lint, production
  build (**753 pages**) and desktop/mobile smoke. That Sentinel intentionally
  omits English advisories; full pre-reader source-backed Sentinel was 0/0/80/0.
- Independently reran five persisted-reader regressions and seven generator
  regressions; all pass. Baseline Code-label fixtures are no longer the only
  evidence: smoke checks the real new book's first/last Code pages and TOC.
- Separate strict browser probe reads ch001/ch013/ch024/ch032/ch040 at 1440/390:
  every rendered paragraph sequence matches the accepted generated Markdown,
  titles/Code labels/navigation match, no horizontal overflow, no unexpected
  console/page error and no non-loopback request. Book search `005` selects only
  ch005. Unreleased ch041 and Investing direct URLs return the intended 404.
- Inspected actual first-chapter desktop/mobile screenshots. No duplicate body
  title, malformed emphasis or obvious reading-layout loss was observed.

## Retention defect caught by acceptance

The first generation silently rewrote the unrelated legacy root manifest's 3,413
CRLFs to LF. Parsed JSON was equal, but the byte-preservation check correctly
failed. Inspector restored **only this task-generated normalization** from the
pre-generation byte backup; no user work was discarded.

The settled low-reasoning fix went to the native Go execution worker after
catalog/location/effective-permission checks. It changed only generator/test files:
retain the root Buffer and validate its semantic agreement with the retained
default-book manifest before cleanup. Unrelated stale root metadata fails closed.
Independent red proof against the original generator produced exactly two new
failures with all five old tests passing; the fixed generator passes all seven.
The full scoped generation/build/smoke then passed again, and the original legacy
manifest's exact bytes now survive. No validation threshold was reduced.

## Limits / landing

Local Windows/Chromium is measured. Linux CI, Firefox/WebKit, merged-SHA CI and
actual live publication are not yet verified. The one-frame saved-dark-theme
flash and raw blocked-metadata serialization backlog remain documented. No
publication cohort is recorded before live verification.

Screenshots/results/logs stay outside the repository in task temp directory
`moonread-first40-z2m2_4o0`: `real-reader-retained-smoke/`, strict
`real-reader-inspector-result.json`, and `generator-retention-red.log`. The original
public snapshot was byte-backed up before generation. The incoming `main` source
metadata work must be preserved during integration; active translation Workers
retain their original worktree/base and are not rebased mid-run. Owner approval
is still required before merge; a local passing command is not that approval.

Pre-commit `git diff --check` reports one source-authored seven-equals UI separator
in ch024 as a possible conflict marker. It matches the raw source and accepted
Markdown; there are no unmerged index entries or opening/closing merge markers.
The separator is retained intentionally, not deleted to silence a tooling heuristic.
