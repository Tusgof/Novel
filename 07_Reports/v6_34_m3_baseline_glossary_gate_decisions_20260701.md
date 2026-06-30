# V6.34 Milestone 3: Baseline Glossary Gate Decisions

Date: 2026-07-01  
Mode: baseline, no tuning before measurement  
Scope: 30 in-sample chapters across DSE, HGD, and IRS

## Decision

For the V6.34 baseline round, all newly scanned glossary candidates are held out. No new glossary notes are created and no existing glossary notes are changed before the baseline translation run.

Reason: baseline must measure the current pipeline behavior before systemic fixes or glossary tuning. Approving new terms before the baseline would contaminate the before/after comparison.

The `glossary_approved` gate is still committed for each sampled chapter so the baseline can proceed using the existing experiment-local glossary copied from each novel.

## Scan Results

| Novel | Run ID | Chapters | New Candidates | Decision |
|---|---|---:|---:|---|
| Deep Sea Embers | `v6-34-m3-dse-baseline-v1` | 10 | 32 | hold all new candidates |
| Horror Game Developer | `v6-34-m3-hgd-baseline-v1` | 10 | 25 | hold all new candidates |
| Infinite Regressor Stories | `v6-34-m3-irs-baseline-v1` | 10 | 122 | hold all new candidates |

## Evidence Paths

- DSE scan artifact: `Deep Sea Embers/04_Work/_experiments/v6_34_m3_dse_baseline_v1/04_Work/_batch/v6-34-m3-dse-baseline-v1/glossary_scan.json`
- HGD scan artifact: `Horror Game Developers/04_Work/_experiments/v6_34_m3_hgd_baseline_v1/04_Work/_batch/v6-34-m3-hgd-baseline-v1/glossary_scan.json`
- IRS scan artifact: `Infinite Regressor Stories/04_Work/_experiments/v6_34_m3_irs_baseline_v1/04_Work/_batch/v6-34-m3-irs-baseline-v1/glossary_scan.json`

## Baseline Guardrail

During Milestone 4 analysis, glossary-related failures should be classified carefully:

- If a failure comes from a candidate deliberately held out here, record it as baseline glossary coverage evidence.
- If the same missing term pattern appears across multiple novels, consider a Layer 0 or Layer 1 fix.
- If it is novel-specific, consider Layer 2 glossary/profile tuning.
- Do not silently patch baseline output; record the defect first.

## Next Step

Commit `glossary_approved` records in the three experiment vaults, then run baseline translation/refinement/QA/format/Sentinel without applying systemic fixes mid-round.
