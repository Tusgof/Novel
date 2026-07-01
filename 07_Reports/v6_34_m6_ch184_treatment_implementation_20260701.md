# V6.34 M6 Treatment Implementation: HGD ch184 QA Hard-Fail

Date: 2026-07-01

## Summary

Implemented the selected ch184 treatment:

- `_resolve_glossary_subset()` now uses boundary-aware matching for alphabetic source keys.
- Added a regression test proving `Enter` does not match `Entering`, while `[Enter]` still matches.
- Reran `ch184-block-001`.

The first rerun from `refine` passed pipeline QA/Sentinel but still contained the previously identified semantic drift on manual inspection. Therefore it was not accepted as final evidence.

The second rerun from `translate` regenerated the literal/refine path and passed:

- QA retry `0`
- latest Sentinel `0/0/0/0`
- no `สะกดรอยตาม`
- no false `ปุ่ม Enter`

## Files Changed

Tracked:

- `Deep Sea Embers/novel_pipeline/pipeline.py`
- `Deep Sea Embers/test_translation.py`

Experiment-only:

- HGD OOS `ch184` artifacts and output were rewritten by rerun-block.

## Verification

| Check | Result |
|---|---|
| `python -m compileall novel_pipeline` | pass |
| `python test_translation.py` | pass |
| `git diff --check` | pass |
| `ch184-block-001` rerun from translate | pass |
| Latest `ch184` QA | pass, retry `0` |
| Latest `ch184` Sentinel | `0/0/0/0` |

Latest Sentinel report:

- `Horror Game Developers/04_Work/_experiments/v6_34_m6_hgd_oos_v1/07_Reports/sentinel_quality_v6-34-m6-hgd-oos-v1_ch184_sentinel_20260701_074411.json`

## Outcome

HGD OOS now has 7/10 chapters complete:

- `ch015`
- `ch046`
- `ch060`
- `ch101`
- `ch131`
- `ch153`
- `ch184`

Current failed blocks: none.

Next pending chapters:

- `ch192`
- `ch226`
- `ch262`

## Lessons

This round exposed a QA false-pass risk: after the first treatment rerun from `refine`, QA and Sentinel passed while a human spot check still found the prior semantic drift. For M6 OOS, risky recovered blocks should get a narrow human/Codex spot check before continuing.
