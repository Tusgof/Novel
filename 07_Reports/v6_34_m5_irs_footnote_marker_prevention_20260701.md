# V6.34 M5 IRS Footnote Marker Prevention

Date: 2026-07-01

## Problem

IRS treatment `ch020` stopped because the source ended with an empty marker:

```text
Footnotes:
```

The provider invented glossary/category notes under Thai `เชิงอรรถ:` and leaked them to final output. Sentinel correctly blocked the chapter with:

- `glossary_note_leakage`
- Evidence: `ดังซอริน: ชื่อตัวละคร`

## Fix

Implemented the smallest cross-pipeline prevention:

- `novel_pipeline.text_utils.strip_empty_trailing_footnote_marker()`
  - applies only to non-CJK source
  - removes only a bare trailing `Footnotes:` marker
  - preserves real source footnote markers such as `Footnotes:\n[1]`
- `split_blocks()` now normalizes empty trailing footnote markers before provider prompts.
- IRS production `.system/config.yaml` now includes blocking Sentinel config so copied IRS experiment vaults do not silently miss runtime Sentinel.

## Verification

Regression:

- `python -m compileall novel_pipeline`: passed
- `PYTHONIOENCODING=utf-8 python test_translation.py`: passed
- New test: `test_split_blocks_strips_empty_trailing_footnotes_marker_only`

Experiment proof:

- Reran `ch020-block-004` from `translate` in `v6-34-m5-irs-treatment-v1`
- QA passed retry 0
- Final chapter output rewritten
- Runtime Sentinel report:
  - `Infinite Regressor Stories/04_Work/_experiments/v6_34_m5_irs_treatment_v1/07_Reports/sentinel_quality_v6-34-m5-irs-treatment-v1_ch020_sentinel_20260701_041436.md`
  - Safe to publish: yes
  - Blocker/Major/Minor/Info: `0/0/0/0`

## Next Action

Continue IRS treatment measurement from `ch067` in the same isolated experiment vault. Stop on any Sentinel blocker/major or provider/manual gate.
