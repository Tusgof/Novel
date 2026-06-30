# V6.34 M5 HGD Treatment Early Stop

Date: 2026-07-01
Run ID: `v6-34-m5-hgd-treatment-v1`
Experiment vault: `Horror Game Developers/04_Work/_experiments/v6_34_m5_hgd_treatment_v1`

## Summary

The HGD treatment rerun was started in a fresh isolated vault.

It stopped safely at `ch024` before reaching the original `ch037` title/glossary defect.

Current status:

- `ch024-block-001`: completed
- current failed block/chapter: `ch024` sentinel gate
- `ch037` and later sampled chapters: pending translation
- production outputs/MoonRead: unchanged

## What Changed Before The Stop

The treatment implementation had already added:

- runtime title/H1 glossary validation
- HGD canonical title map correction: `Velora Art Museum -> พิพิธภัณฑ์ศิลปะเวโลรา`

During treatment execution, a second HGD title-map gap was exposed:

- `The missing piece -> ชิ้นส่วนที่หายไป`

This map entry was added to the runtime HGD title map and the HGD title-normalizer script.

## Stop Evidence

Sentinel report:

- `Horror Game Developers/04_Work/_experiments/v6_34_m5_hgd_treatment_v1/07_Reports/sentinel_quality_v6-34-m5-hgd-treatment-v1_ch024_sentinel_20260630_231030.md`

Findings:

| Severity | Category | Evidence |
|---|---|---|
| blocker | approved_glossary_leakage | `The Nightwalker -> นักเดินราตรี` remained as English parenthetical |
| blocker | approved_glossary_leakage | `Field Agent -> เจ้าหน้าที่ภาคสนาม` remained as English parenthetical |
| blocker | approved_glossary_leakage | `Nightwalker -> นักเดินราตรี` remained as English parenthetical |

Example final output pattern:

- `เจ้าหน้าที่ภาคสนาม (Field Agent)`
- `นักเดินราตรี (The Nightwalker)`

## Layer Classification

| Defect | Layer | Reason |
|---|---|---|
| Missing HGD map for `The missing piece` | Layer 2 HGD title/profile | Specific HGD English title normalization gap |
| Thai plus English glossary parenthetical leakage | Layer 0/2 candidate | The no-English-approved-glossary rule is shared, but the observed terms are HGD-specific |

## Interpretation

This is useful treatment evidence, not a failed workflow:

- The title-map correction let `ch024` assemble with a Thai title.
- Sentinel correctly blocked product-surface glossary leakage.
- The next treatment decision should target approved glossary parenthetical cleanup or formatting/refinement prompt behavior, then rerun from the earliest safe stage.

## Verification Already Run

- `python -m compileall novel_pipeline`: passed after adding `The missing piece`
- `python test_translation.py`: passed after adding `The missing piece`

## Next Step

Analyze whether approved glossary parenthetical leakage should be handled by:

1. deterministic post-format cleanup before final assembly,
2. stronger formatting prompt constraints,
3. Sentinel-only blocking with rerun recovery,
4. or a combination of deterministic cleanup plus Sentinel blocking.

Do not patch `ch024` manually as production output. Keep this as experiment evidence.
