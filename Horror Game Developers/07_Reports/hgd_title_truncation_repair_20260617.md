# HGD Title And Truncation Repair - 2026-06-17

## Scope

- Horror Game Developer final outputs and MoonRead generated content.
- Main reported issues:
  - HGD titles after the earlier published range still displayed English titles.
  - A reader-visible chapter appeared suspiciously short.

## Root Cause

1. HGD `ch036-ch080` had no `04_Work/chXXX/title.json` sidecars, while `ch001-ch035` did.
2. MoonRead title normalization only covered the older title set, so newer titles such as `The game that makes you scream`, `Masquerade ball`, `Little Girl`, and `Evolution` passed through in English.
3. `ch060` and `ch072` previously hit QA hard-fail / force-accept recovery paths after refinement truncation. The old deterministic checks did not compare output length against source length, so truncated final output could still be published.
4. `ch002` also had an older final-output truncation that ended mid-sentence; the new guardrail exposed it during this repair.

## Repairs

- Normalized HGD final-output headings for `ch036-ch080` to Thai, using reader chapter IDs as the displayed chapter number.
- Created title sidecars for `ch036-ch080`.
- Repaired truncated HGD outputs:
  - `ch002`: recovered full translation through the final walkie-talkie line.
  - `ch060`: reran through pipeline until QA passed and final output was rewritten.
  - `ch072`: recovered full translation from a bounded OpenRouter call after repeated pipeline re-refinement truncation; restored glossary terms in the system notification.
- Regenerated MoonRead content: 2 books, 160 available, 0 missing, 0 rejected.

## Prevention Added

- `scripts/check_output_quality_guardrails.py`
  - checks all existing HGD output headings for English fallback markers
  - checks MoonRead HGD manifest titles for English fallback markers
  - compares HGD output length against source length for suspicious truncation
  - flags dangling endings that indicate mid-sentence truncation
- `test_translation.py`
  - added regression coverage for HGD truncation against source length
- `Horror Game Developers/scripts/normalize_hgd_titles.py`
  - reusable title normalization and sidecar writer for HGD output ranges

## Validation

- `python scripts\check_output_quality_guardrails.py`: passed
- `python -m compileall novel_pipeline test_translation.py scripts\check_output_quality_guardrails.py`: passed
- `python test_translation.py`: passed
- `npm.cmd run generate:chapters`: passed, 160 available / 0 missing / 0 rejected
- `npm.cmd run lint`: passed
- `npm.cmd run build`: passed
- `npm.cmd run smoke`: passed
