# V6.19 MoonRead UX/UI Cleanup — Handoff Report

Date: 2026-06-16
Agent: Claude (Opus 4.6)
Scope: reader-web only — no pipeline, provider, or translation changes

## What Was Done

### 1. Synopses rewritten from chapter content

Read DSE ch001-ch003/ch005 and HGD ch001-ch003. Wrote actual story synopses:

- **DSE**: Zhou Ming wakes trapped in a fog-wrapped apartment, discovers a door to the ghost ship of the "Boundless Sea," and becomes Captain Duncan Abnomar — feared by all — navigating a world of gods, mysterious fog, and crumbling reality.
- **HGD**: Seth Thorne, a game programmer who fears ghosts but makes horror games, is forced by a mysterious system into real horror scenarios — surviving a haunted opera, eyeless musicians, and other players who know the rules better than him, all behind a clown mask that will change his fate forever.

### 2. Jargon removed

| Before | After |
|--------|-------|
| `Deep Sea Embers ฉบับแปลไทย` | `เถ้าถ่านแห่งทะเลลึก` |
| `Yuan Tong` | `远瞳 (Yuan Tong)` |
| `Roliascan source` | `CKtalon` |
| `translator` field | removed |
| `"นิยายแปล"` tag | replaced with genre tags |
| `"ที่มา: Private Thai translation pipeline"` | removed from book pages |
| `"MoonRead selection"` eyebrow | `"MoonRead"` |
| MoonRead framework paragraph on book page | removed |

### 3. Homepage rewritten as library page

Old: DSE-focused hero with latest chapters grid and "reading atmosphere" panel.

New: Library-first design with:
- "ชั้นนิยาย" hero section
- Status band showing per-book and total chapter counts
- Equal-treatment book cards with synopsis, tags, and actions
- No single-novel bias

### 4. Navigation updated

- "หน้าแรก" (Home) -> "ชั้นนิยาย" (Library)
- "หน้านิยาย" (Novel page) -> "Deep Sea Embers"

### 5. Smoke test fixed

- `horrorBookTitle` was used inside `page.evaluate()` without being passed as parameter — fixed
- Homepage assertions updated: replaced `hasLatestTitle` with `hasLibraryHero`, switched `hasMoonRead` to use `textContent` instead of `innerText`

## Files Changed

```
reader-web/scripts/generate-chapters.mjs    — synopses, metadata, tags
reader-web/app/page.js                      — complete rewrite (library homepage)
reader-web/app/book/page.js                 — jargon removal
reader-web/app/books/[bookSlug]/page.js     — jargon removal
reader-web/components/SiteHeader.js          — nav labels
reader-web/lib/chapters.js                   — fallback values
reader-web/app/globals.css                   — library-hero styles
reader-web/scripts/smoke-reader.mjs          — test fix + new assertions
```

## Files NOT Changed

- No pipeline code (`novel_pipeline/`, `scripts/`, `test_translation.py`)
- No provider config (`.system/config.yaml`)
- No translation output (`05_Output/`)
- No glossary files
- No dashboard code

## Verification

```
npm run generate:chapters  -> 2 books, 85 available, 0 missing, 0 rejected
npm run lint               -> clean
npm run build              -> 92 static pages
npm run smoke              -> ok: true
```

## What Codex Should Know

1. **IMPLEMENT_PLAN.md updated**: V6.19 is now "MoonRead UX/UI Cleanup" (completed). The old V6.19 (Continue DSE Beyond ch050) is now V6.20.

2. **V6.17.1A2 note**: The plan says "MoonRead regeneration/build/smoke is paused because Claude is editing MoonRead UX/UI" — that pause is now lifted. If HGD English leakage repairs touched `05_Output/`, Codex should rerun `npm run generate:chapters && npm run build && npm run smoke` to pick up any changes.

3. **No conflicts expected**: All changes are in `reader-web/` UI layer. V6.17.1 HGD title/format/leakage work in `05_Output/` and pipeline scripts does not overlap.

4. **Smoke test is stricter now**: The homepage test checks for `.library-hero` element and both book titles. If the homepage structure changes again, update `smoke-reader.mjs` assertions.
