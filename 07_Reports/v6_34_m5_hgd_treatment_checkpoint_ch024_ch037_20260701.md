# V6.34 M5 HGD Treatment Checkpoint: ch024-ch037

Date: 2026-07-01
Run ID: `v6-34-m5-hgd-treatment-v1`
Experiment vault: `Horror Game Developers/04_Work/_experiments/v6_34_m5_hgd_treatment_v1`

## Summary

The treatment run has now passed the original HGD baseline stop point.

Completed:

- `ch024-block-001`
- `ch037-block-001`

Pending:

- `ch066`, `ch103`, `ch132`, `ch142`, `ch170`, `ch196`, `ch225`, `ch250`

Current failed blocks: none.

## Treatment Applied

| Treatment | Result |
|---|---|
| Title/H1 glossary validation | active in final assembly |
| `Velora Art Museum` title map correction | `ch037` H1 now uses `พิพิธภัณฑ์ศิลปะเวโลรา` |
| `The missing piece` title map completion | `ch024` H1 now assembles as Thai title |
| Approved glossary parenthetical cleanup | removes safe `thai_term (source/alias)` leakage after AI formatting |

## Metrics

| Chapter | Baseline / Earlier State | Treatment Checkpoint |
|---|---|---|
| `ch024` | treatment initially blocked with Sentinel `3/0/0/0` from approved glossary English leakage | after cleanup, scoped Sentinel `0/0/0/0` |
| `ch037` | baseline blocked with Sentinel major glossary coverage miss for `Velora Art Museum` / `Art Museum` | scoped Sentinel `0/0/0/0`; H1 uses `พิพิธภัณฑ์ศิลปะเวโลรา` |

## Evidence

- `Horror Game Developers/04_Work/_experiments/v6_34_m5_hgd_treatment_v1/07_Reports/sentinel_quality_v6-34-m5-hgd-treatment-v1_ch024_after_cleanup_20260630_231846.md`
- `Horror Game Developers/04_Work/_experiments/v6_34_m5_hgd_treatment_v1/07_Reports/sentinel_quality_v6-34-m5-hgd-treatment-v1_ch037_sentinel_20260630_232230.md`
- `Horror Game Developers/04_Work/_experiments/v6_34_m5_hgd_treatment_v1/05_Output/ch037/ch037.md`

## Verification

- `python -m compileall novel_pipeline`: passed
- `python test_translation.py`: passed
- treatment scoped Sentinel for `ch024`: `0/0/0/0`
- treatment scoped Sentinel for `ch037`: `0/0/0/0`

## Next Step

Continue M5 treatment rerun for the remaining HGD in-sample chapters. Keep output isolated from production and MoonRead.
