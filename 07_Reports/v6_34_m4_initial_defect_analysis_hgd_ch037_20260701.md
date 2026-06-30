# V6.34 Milestone 4 Initial Defect Analysis: HGD ch037

Date: 2026-07-01  
Run ID: `v6-34-m3-hgd-baseline-v1`  
Experiment vault: `Horror Game Developers/04_Work/_experiments/v6_34_m3_hgd_baseline_v1`

## Summary

The baseline stopped at HGD `ch037` because Sentinel found glossary coverage failures for `Velora Art Museum` / `Art Museum`.

Inspection shows the defect is in the copied title sidecar, not in body translation:

- Source title: `Chapter 37 - Velora Art Museum [2]`
- Approved glossary: `Velora Art Museum -> พิพิธภัณฑ์ศิลปะเวโลรา`
- Title sidecar: `ตอนที่ 37 - พิพิธภัณฑ์ศิลปะเวลอรา`
- Final H1: `# ตอนที่ 37 - พิพิธภัณฑ์ศิลปะเวลอรา`

The output uses `เวลอรา` while the approved glossary requires `เวโลรา`.

## Evidence

| Evidence | Path / Value |
|---|---|
| Source title | `Horror Game Developers/04_Work/_experiments/v6_34_m3_hgd_baseline_v1/03_Raw/ch037/source.json` |
| Production title sidecar copied into experiment | `Horror Game Developers/04_Work/ch037/title.json` |
| Experiment title sidecar | `Horror Game Developers/04_Work/_experiments/v6_34_m3_hgd_baseline_v1/04_Work/ch037/title.json` |
| Experiment output | `Horror Game Developers/04_Work/_experiments/v6_34_m3_hgd_baseline_v1/05_Output/ch037/ch037.md` |
| Experiment Sentinel probe | `07_Reports/sentinel_quality_manual_experiment_ch037_probe_20260630_224633.md` |

## Layer Classification

| Defect | Layer | Reason |
|---|---|---|
| Title sidecar conflicts with approved glossary term | Layer 2: HGD novel profile/artifact | The wrong form is specific to an HGD title sidecar and an HGD glossary entry |
| Sentinel originally scanned production paths from experiment run | Layer 0: multi-novel shared guardrail infrastructure | Any isolated experiment vault could be affected |
| QA passed despite title glossary miss | Layer 0 or Layer 3 | QA operates on block body artifacts and did not validate final H1/title sidecar |

## Treatment Hypotheses

| Hypothesis | Expected Metric Movement | Candidate Fix |
|---|---|---|
| Title sidecars should be validated against approved glossary before final assembly | Fewer Sentinel glossary coverage major findings on H1/title text | Add a deterministic title/glossary guard or include title sidecars in existing output guardrail |
| Experiment Sentinel must scan experiment output, not production output | Sentinel findings become attributable to the current experiment | Keep env override + local registry rule for experiment vaults |
| HGD title sidecars should be repaired when they conflict with approved glossary | HGD title-related glossary misses decrease | Update `ch037/title.json` in the correct production repair milestone, not inside baseline |

## Recommendation

For V6.34 treatment planning:

1. Keep the Sentinel experiment scoping fix as an infrastructure correction; it does not alter translation quality.
2. Treat `Velora Art Museum` as a Layer 2 HGD title/glossary consistency defect.
3. Add a Layer 0 deterministic check that final H1/title text must satisfy approved glossary coverage when the source title contains an approved term.
4. Do not patch the baseline experiment output before treatment comparison.
