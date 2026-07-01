# V6.34 M5 Pre-OOS CJK/Hanja Parenthetical Hardening

Date: 2026-07-01

## Scope

This was a narrow pre-OOS hardening change after cross-novel M5 comparison.

Changed files:

- `Deep Sea Embers/novel_pipeline/text_utils.py`
- `Deep Sea Embers/test_translation.py`

No provider calls, production pipeline runs, production outputs, glossary notes, ledger files, or MoonRead files were modified.

## Cause

IRS treatment completed, but two blocks hard-failed QA because non-CJK English source contained source-script annotations that providers copied into Thai refined output:

- `ch080-block-003`: `군주 (君主)` / `군주 (群主)`
- `ch261-block-001`: Hanja annotations such as `千謠話` / `天寥化`

The existing source cleanup handled the opposite shape, where CJK source text is followed by an English gloss in parentheses. It did not handle English/Korean prose followed by Hanja/Han parenthetical annotations, or quoted source-script terms immediately followed by `meaning ...`.

## Change

Added two non-CJK source normalization paths:

1. `normalize_quoted_cjk_meaning_terms()`
   - Replaces quoted source-script terms followed by English `meaning ...` with `a term meaning ...`.
   - Example: `is '군주 (君主),' meaning a ruler` becomes `is a term meaning a ruler`.

2. `strip_parenthetical_cjk_annotations()`
   - Removes only parenthetical chunks made of CJK/Hanja/Hangul/Kana annotation characters.
   - Preserves normal prose parentheses such as `(skill)` or `(Chapter 1)`.
   - Does not run for `zh`, `ja`, or `ko` source projects.

Both functions run during `split_blocks()` before provider prompts are created.

## Verification

Targeted tests:

```powershell
python - <<targeted equivalent via PowerShell pipe>>
```

Result: passed.

Full regression:

```powershell
python -m compileall novel_pipeline
python test_translation.py
```

Result: passed.

Raw IRS probe:

| Chapter | Source-script chars before split | Source-script chars after split |
|---|---:|---:|
| ch080 | 8 | 0 |
| ch261 | 15 | 0 |

Preflight:

```powershell
novel-pipeline --config ".system/config.yaml" preflight
```

Result: degraded only because the working tree was dirty before commit; providers were ready.

## Decision

This is safe to carry into Milestone 6 OOS because it removes only redundant source annotations from non-CJK projects before provider calls. It should reduce avoidable QA hard-fails without changing translated Thai prose after generation.
