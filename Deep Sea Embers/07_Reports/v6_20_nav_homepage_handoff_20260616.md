# V6.20 MoonRead Nav And Homepage Improvement — Handoff Report

Date: 2026-06-16
Author: Claude (Opus 4.6)
Milestone: V6.20

## Summary

This milestone resolved 3 user-reported UI issues: nav text overlapping the logo on desktop, hardcoded DSE-only nav links that don't scale for multi-book, and missing spacing between homepage book cards. All changes are within `reader-web/` and root docs only — no pipeline, glossary, or translation artifacts were touched.

## Problem

1. The "ชั้นนิยาย" nav link text overlapped with the MoonRead logo on desktop viewports near the 960px breakpoint
2. NavLinks.js hardcoded "Deep Sea Embers" (pointing to DSE-only `/book`) and "สารบัญ" (pointing to DSE-only `/chapters`) — doesn't make sense with 2 novels
3. Homepage book cards had no gap between them
4. SiteFooter.js also had a hardcoded DSE-only `/chapters` link

## Changes Made

### NavLinks.js

| Before | After |
| --- | --- |
| 3 links: "ชั้นนิยาย" (`/`), "Deep Sea Embers" (`/book`), "สารบัญ" (`/chapters`) | 1 link: "หน้าแรก" (`/`) |

Removed unused imports: `BookOpen`, `List`.

### SiteFooter.js

| Before | After |
| --- | --- |
| 2 links: "ชั้นนิยาย" (`/`), "สารบัญ" (`/chapters`) | 1 link: "หน้าแรก" (`/`) |

### globals.css

| Change | Detail |
| --- | --- |
| Nav overlap fix | Added `min-width: 0` to `.site-nav` to prevent grid blowout |
| Mobile nav grid | Changed `repeat(3, minmax(0, 1fr))` to `repeat(auto-fit, minmax(0, 1fr))` — adapts to any number of links |
| Book card spacing | Added `.library-grid` class with `display: flex; flex-direction: column; gap: 20px` |

### app/page.js

Wrapped book card loop in `<div className="library-grid">` for proper 20px gap between cards.

### smoke-reader.mjs

| Before | After |
| --- | --- |
| Clicks "สารบัญ" in primary nav, waits for `/chapters` URL | Uses `page.goto(/chapters)` directly |
| No nav link verification | Checks `hasHomeNavLink` — verifies "หน้าแรก" link exists in primary nav |

`hasHomeNavLink` added to `result.ok` conjunction.

## Verification

All checks pass:

- `npm run generate:chapters` — 2 books, 85 available, 0 missing, 0 rejected
- `npm run lint` — clean
- `npm run build` — 92 pages generated
- `npm run smoke` — `ok: true`, all evidence checks pass including new `hasHomeNavLink: true`

## Files Not Touched

- No pipeline code (`novel_pipeline/`)
- No glossary, source, or translation artifacts
- No config files (`.system/`)
- No ledger or run artifacts

## Doc Updates

- `IMPLEMENT_PLAN.md` — V6.20 milestone recorded as completed; old V6.20 translation continuation bumped to V6.21
- `PROJECT_BRAIN.md` — MoonRead section updated with V6.20 status

## For Codex

The smoke test no longer clicks a nav link to reach `/chapters` — it navigates directly. The nav now has only 1 link ("หน้าแรก"), so any future nav additions should update the mobile grid (`auto-fit` handles this automatically) and the smoke test if the new link should be verified.

The legacy DSE-only routes (`/book`, `/chapters`) still exist and work — they just aren't linked from the global nav anymore. Individual book pages at `/books/[bookSlug]` provide their own TOC sections.
