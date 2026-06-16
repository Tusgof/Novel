# V6.14 MoonRead Publication Check - 2026-06-16

Scope: verify the current reader publication surface without starting any translation run or provider call.

## Published Scope

| book | chapters | status |
| --- | ---: | --- |
| Deep Sea Embers | ch001-ch050 | available |
| Horror Game Developer | ch001-ch035 | available |

Reader import summary after regeneration:

- books: 2
- available chapters: 85
- missing chapters: 0
- rejected chapters: 0

## Commands Run

```powershell
cd "D:\Fogust\Workspace\Novel\Deep Sea Embers\reader-web"
npm.cmd run generate:chapters
npm.cmd run lint
npm.cmd run build
npm.cmd run smoke
```

```powershell
cd "D:\Fogust\Workspace\Novel\Deep Sea Embers"
python scripts\check_output_quality_guardrails.py
python -m compileall novel_pipeline scripts test_translation.py
$env:PYTHONIOENCODING='utf-8'; python test_translation.py
```

## Results

- `npm.cmd run generate:chapters`: passed; generated `2 books, 85 available, 0 missing, 0 rejected`
- `npm.cmd run lint`: passed
- `npm.cmd run build`: passed; Next.js generated 92 static pages
- `npm.cmd run smoke`: passed
  - `ok: true`
  - console errors: none
  - Deep Sea Embers reader route evidence present
  - Horror Game Developer available count: 35
  - bold/italic rendering evidence: `strongCount: 2`, `emCount: 3`
  - mobile overflow: `false`
- `scripts/check_output_quality_guardrails.py`: passed
- `python -m compileall novel_pipeline scripts test_translation.py`: passed
- `python test_translation.py`: passed

## Git Diff Notes

Regeneration changed only generated timestamp metadata in:

- `reader-web/content/generated/books/deep-sea-embers/manifest.json`
- `reader-web/content/generated/books/horror-game-developer/manifest.json`
- `reader-web/content/generated/import-report.md`
- `reader-web/content/generated/library.json`
- `reader-web/content/generated/manifest.json`

No generated chapter Markdown content changed in this verification pass.

## Decision

V6.14 publication check passes for the current published scope. MoonRead is trustworthy for:

- Deep Sea Embers `ch001-ch050`
- Horror Game Developer `ch001-ch035`

This report does not approve a new translation batch, provider route change, or formatter behavior change.
