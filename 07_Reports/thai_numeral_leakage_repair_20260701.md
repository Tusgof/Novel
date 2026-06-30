# Thai Numeral Leakage Repair - 2026-07-01

## Scope

- User-reported issue: Thai numerals appeared in IRS output often enough to require a sustainable fix.
- Audit scope: current final outputs for DSE, HGD, IRS; MoonRead generated content; IRS ignored archives/experiment artifacts for root-cause separation.

## Findings

- Current IRS product output (`Infinite Regressor Stories/05_Output`, excluding `_archive`) had no Thai numerals.
- Current IRS MoonRead generated content had no Thai numerals.
- Old IRS archive/experiment outputs still contain Thai numerals, but they are not current product surface.
- Current DSE product output had a related product leak pattern:
  - Thai numeral title-tail leak in `Deep Sea Embers/05_Output/ch175/ch175.md`
  - Duplicate title-like body tails in DSE `ch167`, `ch169`, `ch174`, `ch175`, `ch176`, `ch177`, and `ch178`
  - The same stale lines had propagated into MoonRead generated DSE chapters.
- The Thai-numeral line was `บทที่ ๑๗๕ เมฆดำปกคลุมเมือง`.

## Root Cause

1. The existing Thai-numeral guardrail was configured only as an IRS registry forbidden-output pattern.
2. DSE could therefore leak Thai numerals without being blocked.
3. The specific DSE leak came from provider output in late DSE blocks, where source title-like tails were preserved as prose. One of those tails was formatted with Thai numerals.
4. The old duplicate-title guardrail only checked the paragraph immediately below the H1 heading, so title-like tails near the end of a chapter were not blocked.
5. MoonRead regenerated from final output, so the stale product leak propagated into reader content.

## Repair

- Removed duplicate title tails from DSE final output and source artifacts for:
  - `ch167`
  - `ch169`
  - `ch174`
  - `ch175`
  - `ch176`
  - `ch177`
  - `ch178`
- Regenerated MoonRead chapters.
- Added a global product-surface Thai numeral guardrail in `scripts/check_output_quality_guardrails.py`.
- Extended duplicate-title guardrail to reject title-like body paragraphs anywhere after H1, not only immediately below H1.
- Added regression coverage in `test_translation.py`.

## Prevention

- `check_thai_numeral_leakage()` now scans all registered novel final outputs and MoonRead generated chapters.
- The check includes legacy generated reader path for legacy-default novels.
- `check_duplicate_title_paragraphs()` now catches late title-like body tails such as `บทที่ N ...` and `**[บทที่ N ...]**`.
- Future product output should use Arabic digits across novels unless a later explicit policy changes that.

## Verification

- `python "Deep Sea Embers/scripts/check_output_quality_guardrails.py" --novel deep-sea-embers --chapters ch167-ch178`: passed
- `python "Deep Sea Embers/scripts/check_output_quality_guardrails.py" --novel infinite-regressor-stories --chapters ch001-ch050`: passed
- `rg -n "[๐๑๒๓๔๕๖๗๘๙]" "Deep Sea Embers/05_Output" "Horror Game Developers/05_Output" "Infinite Regressor Stories/05_Output" "MoonRead/content/generated" -g "!**/_archive/**"`: no matches
- `rg -n "^\*?\*?\[?บทที่ [0-9๐๑๒๓๔๕๖๗๘๙]+" "Deep Sea Embers/05_Output" "MoonRead/content/generated/books/deep-sea-embers/chapters" "MoonRead/content/generated/chapters"`: no matches
- `python -m compileall "Deep Sea Embers/novel_pipeline"`: passed
- `$env:PYTHONIOENCODING='utf-8'; python test_translation.py`: passed
- scoped `npm.cmd run publish:verify` for DSE `ch175`: passed
- `npm.cmd run lint`: passed
- `npm.cmd run build`: passed
- `npm.cmd run smoke`: passed
