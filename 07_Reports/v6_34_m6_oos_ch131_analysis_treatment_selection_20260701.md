# V6.34 M6.3 OOS Analysis And Treatment Selection

Date: 2026-07-01

## Summary

HGD OOS stopped at `ch131` on a Sentinel major glossary coverage finding. Analysis shows this is not a provider outage or translation truncation. It is a glossary conflict that should be fixed at two layers before any OOS resume:

1. Layer 0: glossary conflict detector must flag when one approved note's `original_term` is used as another approved note's alias with a different Thai term.
2. Layer 2: HGD glossary must remove the bad `Containment Department` alias from `Containment Sector.md` so `Containment Department.md` can be the canonical department term.

## Evidence

OOS stop report:

- `07_Reports/v6_34_m6_oos_hgd_stop_ch131_glossary_conflict_20260701.md`

Sentinel report:

- `Horror Game Developers/04_Work/_experiments/v6_34_m6_hgd_oos_v1/07_Reports/sentinel_quality_v6-34-m6-hgd-oos-v1_ch131_sentinel_20260701_065128.md`

Existing glossary conflicts report:

- `Horror Game Developers/04_Work/_experiments/v6_34_m6_hgd_oos_v1/07_Reports/v6_34_m6_hgd_oos_glossary_conflicts_after_ch131_stop.md`

## Finding

| Item | Evidence |
|---|---|
| Source term | `Containment Department` |
| Required direct glossary term | `Containment Department -> แผนกกักกัน` |
| Output used | `ภาคส่วนกักกัน` |
| Conflicting note | `Containment Sector -> ภาคส่วนกักกัน` |
| Bad alias | `Containment Department` appears under `Containment Sector.md` aliases |

## Detector Gap

The existing `glossary-conflicts` report already exits as actionable when it finds some conflict classes, but it did not flag this exact issue as a distinct collision.

Reason: current alias collision logic checks alias ownership among aliases. It does not compare:

- approved note A `original_term`
- against approved note B `aliases`
- when A and B have different `thai_term`

This allowed `Containment Department` to exist as both:

- direct approved original term: `แผนกกักกัน`
- alias of another approved term: `ภาคส่วนกักกัน`

## Layer Decision

| Layer | Decision | Reason |
|---|---|---|
| Layer 0 multi-novel | Add source-surface collision detection to `glossary-conflicts` | Any novel can accidentally approve a term that already exists as another note's alias |
| Layer 1 language | No change | This is not Thai/English grammar or language-specific style |
| Layer 2 HGD | Remove `Containment Department` and `The Containment Department` aliases from `Containment Sector.md` | HGD glossary is internally inconsistent |
| Layer 3 run-local | No manual output patch | OOS output must not be patched before policy fix |
| Layer 4 MoonRead | No change | Experiment output is not reader content |

## Selected Treatment

Implement both selected fixes before any OOS resume:

1. Extend `build_glossary_conflicts_report()` to include original/alias source-surface collisions where approved entries map the same source surface to different Thai terms.
2. Add regression test covering `Containment Department` as original and alias of `Containment Sector`.
3. Clean HGD glossary by removing only the conflicting aliases from `Containment Sector.md`.
4. Copy the cleaned glossary note into the HGD OOS experiment vault before rerunning the affected OOS slice.

## Expected Metric Movement

| Metric | Expected movement |
|---|---|
| glossary conflict report | explicitly flags source-surface collisions before translation |
| HGD ch131 Sentinel major | should clear after rerun from translate/refine with corrected glossary subset |
| production safety | improves because future duplicated alias/original terms become visible at glossary gate |

## Next Action

Implement the selected treatment surgically, run targeted tests, then rerun HGD OOS from the earliest affected safe stage after documenting the change.
