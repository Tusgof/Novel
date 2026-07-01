# V6.34 M6 OOS Stop: HGD ch131 Glossary Conflict

Date: 2026-07-01

## Summary

Milestone 6.2 out-of-sample translation started with Horror Game Developer in the isolated experiment vault `Horror Game Developers/04_Work/_experiments/v6_34_m6_hgd_oos_v1`.

The run safely stopped after `ch131` because blocking Sentinel reported a major glossary coverage finding. This is out-of-sample evidence and was not repaired mid-round.

## Run State

| Item | Value |
|---|---|
| Run ID | `v6-34-m6-hgd-oos-v1` |
| Experiment vault | `Horror Game Developers/04_Work/_experiments/v6_34_m6_hgd_oos_v1` |
| Completed chapters before stop | `ch015`, `ch046`, `ch060`, `ch101`, `ch131` |
| Current failed chapter | `ch131` |
| Remaining pending chapters | `ch153`, `ch184`, `ch192`, `ch226`, `ch262` |
| Current failed blocks | `ch131` chapter-level Sentinel record |
| Production output changed | No |
| MoonRead changed | No |

## Failure Evidence

Sentinel report:

- `Horror Game Developers/04_Work/_experiments/v6_34_m6_hgd_oos_v1/07_Reports/sentinel_quality_v6-34-m6-hgd-oos-v1_ch131_sentinel_20260701_065128.md`
- Counts: blocker/major/minor/info `0/1/0/0`
- Finding: `glossary_coverage_missing`
- Evidence: `Containment Department -> แผนกกักกัน; glossary=Containment Department.md`

Source `ch131` contains:

> "So you want to send some of our best talents to the Containment Department?"

Final output used:

- `ภาคส่วนกักกัน`

instead of:

- `แผนกกักกัน`

## Cause Classification

Layer: Layer 2 novel glossary conflict, with possible Layer 0 conflict-detector gap.

Reason:

- `Containment Department.md` approves `Containment Department -> แผนกกักกัน`.
- `Containment Sector.md` approves `Containment Sector -> ภาคส่วนกักกัน`.
- `Containment Sector.md` also lists `Containment Department` and `The Containment Department` as aliases.
- The model output followed the older alias/canonical direction (`ภาคส่วนกักกัน`) while Sentinel enforced the newer direct approved term (`แผนกกักกัน`).

This is a real OOS glossary consistency defect, not provider outage and not source loss.

## OOS Policy Decision

No repair was applied during M6.2.

Reason: the M6 OOS round is designed to measure generalization. Fixing the glossary conflict immediately would tune on OOS data before comparison.

## Next Action

Move to M6.3 analysis:

1. Count this as an OOS major glossary conflict.
2. Compare against in-sample treatment defects.
3. Decide whether the fix belongs in Layer 2 HGD glossary cleanup only, or whether Layer 0 needs a duplicate-original/alias conflict detector before production scaling.
4. Do not resume OOS translation until the analysis decision is documented.
