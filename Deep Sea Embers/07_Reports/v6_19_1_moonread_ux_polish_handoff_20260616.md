# V6.19.1 MoonRead UX/UI Polish And Cover Art — Handoff Report

Date: 2026-06-16
Author: Claude (Opus 4.6)
Milestone: V6.19.1

## Summary

This milestone resolved 13 UX/UI issues identified after the V6.19 library-first redesign and integrated Codex-generated cover art for both novels. All changes are within `reader-web/` and root docs only — no pipeline, glossary, or translation artifacts were touched.

## Changes Made

### Thai Localization

| File | Change |
| --- | --- |
| `app/chapters/page.js` | Eyebrow "Table of contents" → "สารบัญ"; removed technical jargon from description |
| `app/books/[bookSlug]/chapters/page.js` | Same jargon fix as DSE chapters page |
| `components/ReaderShell.js` | Theme labels "Paper/Sepia/Night" → "กระดาษ/ซีเปีย/กลางคืน" |
| `app/layout.js` | Metadata description changed to Thai |

### localStorage Key Migration

| File | Change |
| --- | --- |
| `components/ReaderShell.js` | Reads from `moonread-reader-settings` with `dse-reader-settings` fallback; writes only to new key |

### New Components

| File | Purpose |
| --- | --- |
| `components/NavLinks.js` (new) | Client component using `usePathname()` for active nav link highlighting |
| `components/SiteFooter.js` (new) | Site-wide footer with brand, nav links, tagline |

### Component Updates

| File | Change |
| --- | --- |
| `components/SiteHeader.js` | Refactored to import NavLinks instead of inline link rendering |
| `app/page.js` | Swapped primary/secondary buttons; added `library-synopsis` class |
| `app/book/page.js` | Added SiteFooter |
| `app/books/[bookSlug]/page.js` | Added SiteFooter; made `logo-cover` class conditional |
| `app/chapters/page.js` | Added SiteFooter |
| `app/books/[bookSlug]/chapters/page.js` | Added SiteFooter |

### CSS (`app/globals.css`)

- `.site-nav a.active` — active nav link style
- `.library-hero` — border-bottom separator
- `.status-band strong` — gold color for stat numbers
- `.library-cover.logo-cover` — dark gradient placeholder for books without cover art
- `.library-synopsis` — 3-line clamp
- `.drawer-panel` — uses `var(--paper-strong)` instead of hardcoded color
- `.site-footer` — full footer styles
- Mobile: `.library-cover { max-width: 200px }` in `@media (max-width: 960px)`

### Cover Art Integration

| File | Change |
| --- | --- |
| `public/images/deep-sea-embers-cover.png` | Replaced with Codex-generated cover art |
| `public/images/horror-game-developer-cover.png` | New Codex-generated cover art |
| `scripts/generate-chapters.mjs` | HGD cover path changed from `/images/moonread-logo.svg` to `/images/horror-game-developer-cover.png` |

Cover art source: `D:\Fogust\Workspace\Novel\00_Assets\cover_art\20260616\`

### Test Updates

| File | Change |
| --- | --- |
| `scripts/smoke-reader.mjs` | "Night" → "กลางคืน" button label; `dse-reader-settings` → `moonread-reader-settings`; scoped nav selector to `Primary navigation` to disambiguate from footer |

## Verification

All checks pass:

- `npm run generate:chapters` — 2 books, 85 available, 0 missing, 0 rejected
- `npm run lint` — clean
- `npm run build` — 92 pages generated
- `npm run smoke` — `ok: true`, all evidence checks pass

## Files Not Touched

- No pipeline code (`novel_pipeline/`)
- No glossary, source, or translation artifacts
- No config files (`.system/`)
- No ledger or run artifacts

## Doc Updates

- `IMPLEMENT_PLAN.md` — V6.19.1 milestone recorded as completed
- `PROJECT_BRAIN.md` — MoonRead section updated with V6.19.1 status and cover art source

## For Codex

If you need to regenerate MoonRead after pipeline changes, run:

```powershell
cd reader-web
npm run generate:chapters
npm run lint
npm run build
npm run smoke
```

The smoke test now expects Thai theme labels and the `moonread-reader-settings` localStorage key. The nav link selector is scoped to `Primary navigation` aria-label to avoid conflict with footer links.
