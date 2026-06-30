# IRS Thai Numeral Audit - 2026-07-01

## Scope

- Novel: Infinite Regressor Stories
- Product range checked: `ch001-ch050`
- Surfaces checked:
  - `Infinite Regressor Stories/05_Output/ch*/ch*.md`
  - `MoonRead/content/generated/books/infinite-regressor-stories/chapters/ch*.md`
  - IRS archive/work paths were searched separately to identify historical leftovers.

## Result

Current IRS product output is clean.

- `05_Output/ch001-ch050`: no Thai numerals found.
- MoonRead generated IRS book chapters: no Thai numerals found.
- Scoped output guardrail passed:
  - `python "Deep Sea Embers\scripts\check_output_quality_guardrails.py" --novel infinite-regressor-stories --chapters ch001-ch050`
- Scoped Sentinel passed:
  - `07_Reports/sentinel_quality_irs-thai-numeral-audit-ch001-ch050_20260630_203654.md`
  - blocker/major/minor/info: `0/0/0/0`

## Findings

Thai numerals still exist only in old archived IRS artifacts:

- `Infinite Regressor Stories/05_Output/_archive/clean_retranslate_ch001_ch050_20260630_075430/...`
- `Infinite Regressor Stories/04_Work/_archive/clean_retranslate_ch001_ch050_20260630_075430/...`

Those archived files preserve pre-repair drafts and are not the current product surface. They were not edited.

## Cause

The earlier IRS clean retranslation allowed AI refinement/formatting providers to stylistically rewrite Arabic numerals into Thai numerals. The old archive preserves that pre-normalized state.

## Repair

No additional product repair was needed in this audit because the current final output and MoonRead generated IRS chapters were already normalized to Arabic digits.

## Prevention

The recurrence guard is already active:

- `00_Config/novel_registry.json` contains an IRS `forbidden_output_patterns` rule rejecting `[๐-๙]`.
- `Deep Sea Embers/scripts/check_output_quality_guardrails.py` applies registry-driven forbidden output patterns to both final output and MoonRead generated book chapters.
- `Deep Sea Embers/test_translation.py` has regression coverage for IRS Thai numerals.
- Future IRS checks should stay scoped:
  - `--novel infinite-regressor-stories --chapters <range>`

## Verification

- `python -m compileall "Deep Sea Embers\novel_pipeline"`: passed
- `PYTHONIOENCODING=utf-8; python test_translation.py` from `Deep Sea Embers`: passed
- `git diff --check`: passed

