# Publish to MoonRead

**What.** MoonRead is the Next.js reader in `MoonRead/`. `generate:chapters` imports verified chapters from each registered novel's output folder (per `00_Config/novel_registry.json`) into `MoonRead/content/generated/`; pushing that content to GitHub lets Vercel deploy it.

**How the owner asks.** "ช่วยอัป [เรื่อง] ตอน [ช่วง] ขึ้น MoonRead" — see `NOVEL_OPERATOR_GUIDE.md` §4.

**Drive it** (from `MoonRead/`):
```
npm install
SENTINEL_NOVEL=<novel-id> SENTINEL_CHAPTERS=ch211-ch215 npm run publish:verify
```
`publish:verify` runs `generate:chapters`, the Sentinel gate (`MoonRead/scripts/run-sentinel-gate.mjs`), lint, build, and the reader smoke test (`MoonRead/scripts/smoke-reader.mjs`). On Windows PowerShell set the two variables with `$env:` before `npm.cmd run publish:verify`.

**Verify.** `publish:verify` exits successfully; the generated chapter files for the scope are in `MoonRead/content/generated/` and are committed with the change. After the push, the deployed reader shows the new chapters.

**Gotchas.**
- Publishing is outward-facing: it needs the owner's request for this scope.
- The Sentinel gate refuses to run without `SENTINEL_NOVEL` and `SENTINEL_CHAPTERS` unless `SENTINEL_ALLOW_FULL=1` is set on purpose.
- What MoonRead shows is controlled per novel in `00_Config/novel_registry.json`: `reader.enabled` and the `first_chapter` / `last_chapter` range. Check them before publishing a new title or range.
