# V6.34 M5 HGD Treatment: ch132 BOM Glossary Repair

Date: 2026-07-01
Run ID: `v6-34-m5-hgd-treatment-v1`
Experiment vault: `Horror Game Developers/04_Work/_experiments/v6_34_m5_hgd_treatment_v1`

## Summary

HGD treatment rerun progressed through `ch066` and `ch103`, then stopped at `ch132` because Sentinel found missing approved glossary coverage.

Root cause was not source loss. The source contained `Hoarding Department`, `Collection Department`, `Sarah Sorloth`, and `Sarah`. The pipeline failed to load the relevant glossary notes because several Markdown notes started with a UTF-8 BOM before frontmatter (`\ufeff---`), causing `parse_glossary_note()` to return `None`.

## Defect Classification

| Defect | Layer | Evidence | Treatment |
|---|---|---|---|
| BOM-prefixed glossary notes skipped by parser | Layer 0 multi-novel | `Sarah.md`, `Sarah Sorloth.md`, `Hoarding Department.md`, and `Collection Department.md` parsed as `None` before parser fix | `parse_glossary_note()` now strips UTF-8 BOM before frontmatter check |
| HGD loose variants not recorded as rejected variants | Layer 2 novel-specific | output used `ซาร่าห์`, `ซาร่าห์ ซอร์ลอธ`, `แผนกสะสม`, `แผนกจัดเก็บ` | HGD glossary notes now record those forms in `rejected_variants` |
| Kaelen note body contradicted approved `thai_term` | Layer 2 novel-specific | `Kaelen.md` frontmatter had `thai_term: เคเลน`, body said `Use แคเลน consistently` | body now matches approved `เคเลน` |

## Metrics

| Chapter | Before Treatment | After Treatment |
|---|---|---|
| `ch132` | Sentinel `3/2/0/0`, safe to publish: no | Sentinel `0/0/0/0`, safe to publish: yes |

Current treatment status after repair:

- Completed: `ch024`, `ch037`, `ch066`, `ch103`, `ch132`
- Current failed blocks: none
- Pending: `ch142`, `ch170`, `ch196`, `ch225`, `ch250`

## Evidence

- Latest pass report: `Horror Game Developers/04_Work/_experiments/v6_34_m5_hgd_treatment_v1/07_Reports/sentinel_quality_v6-34-m5-hgd-treatment-v1_ch132_sentinel_20260701_000506.md`
- Output proof: `Horror Game Developers/04_Work/_experiments/v6_34_m5_hgd_treatment_v1/05_Output/ch132/ch132.md`
- Updated parser: `Deep Sea Embers/novel_pipeline/glossary_support.py`
- Regression tests: `Deep Sea Embers/test_translation.py`

## Verification

- `python -m compileall novel_pipeline`: passed
- `python test_translation.py`: passed
- `novel-pipeline --config ".system/config.yaml" rerun-block --run-id v6-34-m5-hgd-treatment-v1 --block-id ch132-block-001 --from-stage refining`: passed
- `novel-pipeline --config ".system/config.yaml" status --run-id v6-34-m5-hgd-treatment-v1`: no current failed blocks

## Next Step

Continue M5 treatment rerun in the same isolated vault from `ch142`.
