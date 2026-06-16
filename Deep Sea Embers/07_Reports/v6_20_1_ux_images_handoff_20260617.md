# V6.20.1 MoonRead UX/UI Enhancement — Images, 404, OG — Handoff Report

Date: 2026-06-17
Author: Claude (Opus 4.6)
Milestone: V6.20.1

## Summary

This milestone added structural support for branded artwork across MoonRead: hero banner on homepage, custom 404 page with illustration, Open Graph / Twitter Card metadata for social sharing, and apple-touch-icon for iOS. All code and CSS changes are live and verified. Placeholder 1x1 PNGs are in place — the user will replace them with their actual processed images.

## Changes Made

### app/layout.js

| Change | Detail |
| --- | --- |
| `metadataBase` | Added `https://moonread.vercel.app` to suppress Next.js OG resolution warnings |
| `icons.apple` | Added `/images/apple-touch-icon.png` reference |
| `openGraph` | Added full OG metadata: title, description, siteName, image (1200x630), locale `th_TH`, type `website` |
| `twitter` | Added Twitter card metadata: `summary_large_image`, title, description, image |

### app/not-found.js

| Before | After |
| --- | --- |
| Text-only: "ไม่พบตอนนี้", link to `/chapters` | Illustration (`/images/404-cat.png`), "ไม่พบหน้านี้", link to `/` |

Added `next/image` import, `.not-found-art` wrapper for the illustration.

### app/page.js

| Change | Detail |
| --- | --- |
| Hero section | Added `has-banner` class to `.library-hero` for CSS background-image support |

### app/globals.css

| Change | Detail |
| --- | --- |
| `.library-hero.has-banner` | Background image `/images/hero-banner.png`, `contain`, right-aligned, `min-height: 220px` |
| `.library-hero.has-banner .hero-copy` | `position: relative; z-index: 1` to stay above background |
| `.not-found-art` | `margin-bottom: 24px; opacity: 0.88` |
| `.not-found-art img` | `max-width: 260px; width: 100%` |
| `.not-found p` | Added `max-width: 360px` |
| 960px breakpoint | Banner shrinks to `background-size: 40%` |
| 680px breakpoint | Banner hidden (`background-image: none`) on mobile |

### scripts/smoke-reader.mjs

| Change | Detail |
| --- | --- |
| OG evidence | Checks `og:title`, `og:image`, `twitter:card` meta tags on homepage |
| 404 evidence | Navigates to `/this-page-does-not-exist-404`, checks `.not-found` class, `.not-found-art img`, heading text "ไม่พบหน้านี้", home link `href="/"` |
| Console error handling | Splits errors into pre-404 (unexpected) and post-404 (expected from intentional 404 navigation) |
| Screenshots | Added `moonread-404.png` |
| `result.ok` | Added `ogEvidence.hasOgTitle`, `ogEvidence.hasOgImage`, `notFoundEvidence.*` to conjunction |

### Placeholder images created

| Path | Purpose | User action needed |
| --- | --- | --- |
| `public/images/hero-banner.png` | Homepage hero background | Replace with wide banner (cat/moon/flowers, dark bg) |
| `public/images/og-image.png` | Social sharing preview | Replace with 1200x630 crop of banner |
| `public/images/404-cat.png` | 404 page illustration | Replace with sleeping cat (green screen removed → transparent PNG) |
| `public/images/apple-touch-icon.png` | iOS home screen icon | Replace with 180x180 from square MoonRead logo |

All 4 are currently 1x1 transparent placeholder PNGs so the build and smoke test pass.

## Verification

All checks pass:

- `npm run generate:chapters` — 2 books, 160 available, 0 missing, 0 rejected
- `npm run lint` — clean
- `npm run build` — 167 pages generated, no warnings
- `npm run smoke` — `ok: true`, all evidence checks pass:
  - `ogEvidence`: `hasOgTitle: true`, `hasOgImage: true`, `hasTwitterCard: true`
  - `notFoundEvidence`: `hasNotFoundClass: true`, `hasIllustration: true`, `hasHeading: true`, `hasHomeLink: true`
  - All pre-existing checks continue to pass

## Files Not Touched

- No pipeline code (`novel_pipeline/`)
- No glossary, source, or translation artifacts
- No config files (`.system/`)
- No ledger or run artifacts

## User Action Required

The user needs to replace the 4 placeholder PNGs in `MoonRead/public/images/` with actual processed images:

1. **hero-banner.png**: The wide banner image (cat on book, moon, flowers, constellations, dark background). No processing needed — use as-is from original.
2. **og-image.png**: Crop/resize the wide banner to 1200x630 for social sharing.
3. **404-cat.png**: The sleeping cat on book image — remove green screen background to get transparent PNG.
4. **apple-touch-icon.png**: Crop/resize the square MoonRead logo to 180x180 PNG.

After replacing, re-run `npm run build && npm run smoke` to verify.

## For Codex

- The hero banner uses CSS `background-image` (not Next.js `<Image>`) so it doesn't go through the image optimizer. This is intentional — it's decorative and right-aligned, not critical content.
- The 404 illustration uses Next.js `<Image>` with fixed `width={260} height={260}`.
- OG metadata uses `metadataBase: new URL("https://moonread.vercel.app")`. Update this if the production URL changes.
- The smoke test splits console errors at the 404 navigation boundary to avoid false failures from expected 404 resource errors. `notFoundConsoleErrors` in the result shows these expected errors separately.
- The hero banner is hidden on mobile (≤680px) to avoid layout issues with small viewports.
