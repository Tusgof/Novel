# Publish to MoonRead

**What.** MoonRead is the Next.js reader in `MoonRead/`. `generate:chapters` imports verified chapters from each registered novel's output folder (per `00_Config/novel_registry.json`) into `MoonRead/content/generated/`; pushing that content to GitHub lets Vercel deploy it.

**How the owner asks.** "ช่วยอัป [เรื่อง] ตอน [ช่วง] ขึ้น MoonRead" — see `NOVEL_OPERATOR_GUIDE.md` §4.

**Drive it** (from `MoonRead/`):
```
npm install
SENTINEL_NOVEL=<novel-id> SENTINEL_CHAPTERS=ch211-ch215 npm run publish:verify
```
`publish:verify` runs `generate:chapters`, the Sentinel gate (`MoonRead/scripts/run-sentinel-gate.mjs`), lint, build, and the reader smoke test (`MoonRead/scripts/smoke-reader.mjs`). On Windows PowerShell set the two variables with `$env:` before `npm.cmd run publish:verify`.
`SENTINEL_NOVEL` also scopes generation: only the selected enabled slug(s) are
rebuilt. Other books retain their existing manifest/chapter bytes, are labeled
  as retained/not revalidated in the import report, and must already match their
  registry range. Unknown/disabled selections or a missing retained snapshot fail
  before cleaning. Omitting the variable still requests full-library regeneration.
- A retained legacy/default root manifest also keeps its exact bytes (including
  CRLF) and must agree semantically with the retained per-book manifest before
  cleanup. A stale root is blocked, not silently normalized or regenerated.

**Verify.** `publish:verify` exits successfully; the generated chapter files for the scope are in `MoonRead/content/generated/` and are committed with the change. After the push, the deployed reader shows the new chapters.

**Gotchas.**
- Publishing is outward-facing: it needs the owner's request for this scope.
- The Sentinel gate refuses to run without `SENTINEL_NOVEL` and `SENTINEL_CHAPTERS` unless `SENTINEL_ALLOW_FULL=1` is set on purpose.
- What MoonRead shows is controlled per novel in `00_Config/novel_registry.json`: `reader.enabled` and the `first_chapter` / `last_chapter` range. Check them before publishing a new title or range.
- `reader.code_chapters` lists the exact episode IDs labeled `[Code]`; all others
  retain their configured Lean/Pipe behavior. `npm run test:generate` tests label
  precedence, scoped preservation, bad selected content and invalid scope/range.
- For persisted-state bugs, build first, then run `npm run test:reader`: it seeds
  saved progress/settings and checks hydration, restoration, TOC numbers and dialog
  keyboard/focus behaviour. Reader CI installs the declared Chromium and runs it.
- Text equality does not prove visible line breaks. `test:reader` also checks actual
  glyph positions in multiline status/item blocks at desktop/mobile widths. The
  reader preserves authored newlines with `white-space: pre-line`; do not rewrite
  accepted Markdown or insert extra blank paragraphs to mask a rendering defect.
- Set `MOONREAD_SMOKE_OUTPUT_DIR` to task-owned storage outside the repository
  before `npm run smoke`; the printed screenshot paths use that actual directory.
  Baseline Code-label fixtures do not prove new-book runtime until scoped content
  generation and a fresh reader smoke include those accepted chapters.
