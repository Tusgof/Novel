# V6.34 M6 Treatment Implementation: HGD ch131 Glossary Conflict

Date: 2026-07-01

## Summary

Implemented the selected M6.3 treatment for the HGD `ch131` OOS glossary conflict.

Changes:

- Added Layer 0 source-surface collision detection to `glossary-conflicts`.
- Added regression coverage for an approved `original_term` colliding with another approved note's alias when Thai terms differ.
- Removed the conflicting `Containment Department` aliases from HGD `Containment Sector.md`.
- Synced the cleaned glossary note into the isolated HGD OOS experiment vault.
- Reran `ch131-block-001` from `refine`.

## Files Changed

Tracked:

- `Deep Sea Embers/novel_pipeline/reports.py`
- `Deep Sea Embers/test_translation.py`
- `Horror Game Developers/01_Glossary/Containment Sector.md`

Experiment-only:

- `Horror Game Developers/04_Work/_experiments/v6_34_m6_hgd_oos_v1/01_Glossary/Containment Sector.md`
- HGD OOS `ch131` artifacts and output were rewritten by `rerun-block`

## Verification

| Check | Result |
|---|---|
| `python -m compileall novel_pipeline` | pass |
| `python test_translation.py` | pass |
| `git diff --check` | pass |
| HGD OOS `ch131` rerun | pass |
| Latest `ch131` Sentinel | `0/0/0/0` |

Latest Sentinel report:

- `Horror Game Developers/04_Work/_experiments/v6_34_m6_hgd_oos_v1/07_Reports/sentinel_quality_v6-34-m6-hgd-oos-v1_ch131_sentinel_20260701_071217.json`

## Outcome

`ch131` no longer has a current failed Sentinel state. The run now has 5/10 HGD OOS chapters complete and can resume from `ch153-block-001` after this treatment is committed.

## Remaining Evidence

The improved conflict detector now also surfaces other HGD source-surface collisions, such as person-name alias collisions:

- `Kaelen`
- `Malovia Island`
- `Sarah`
- `Serelith`

These were not the cause of `ch131`, but they should remain visible in later glossary review. They are not a reason to block the ch131 treatment commit.
