# V6.34 M5 DSE Treatment V2 Completion Report

Date: 2026-07-01

## Scope

- Novel: Deep Sea Embers
- Experiment vault: `Deep Sea Embers/04_Work/_experiments/v6_34_m5_dse_treatment_v2`
- Run ID: `v6-34-m5-dse-treatment-v2`
- Sample chapters: `ch017`, `ch034`, `ch048`, `ch060`, `ch081`, `ch094`, `ch114`, `ch142`, `ch161`, `ch168`
- Purpose: rerun the DSE in-sample treatment slice after invalidating prior copied experiment vaults with stale/off-by-one raw source.
- Production/MoonRead impact: none. This was experiment-only.

## Source Parity Gate

`scripts/verify_experiment_source_parity.py` was run against the exact sampled chapters before and after treatment execution.

Final result:

```text
Checked 10 chapters
Mismatches: 0
```

This confirms the experiment vault raw source matched current production `Deep Sea Embers/03_Raw` for the sampled chapters.

## Final Status

`novel-pipeline status --run-id v6-34-m5-dse-treatment-v2` reported:

- Completed blocks: 56/56
- Current failed blocks: none
- Failed blocks: none
- Historical failed records: 1
- Manual actions needed: none
- Final outputs exist for all 10 sampled chapters inside the experiment vault.

## Stage Counts

| Stage | Completed | Failed |
|---|---:|---:|
| fetched | 10 | 0 |
| glossary_scanned | 10 | 0 |
| glossary_approved | 10 | 0 |
| translating | 56 | 0 |
| refining | 62 | 1 |
| qa | 56 | 0 |
| formatting | 56 | 0 |
| completed | 56 | 0 |
| sentinel | 55 | 0 |

The one failed refining record was historical and recovered:

- `ch094-block-005`: OpenRouter returned an empty assistant message after 42.35 seconds.

## Provider Usage

| Provider | Stage | Completed | Failed |
|---|---|---:|---:|
| local | fetched | 10 | 0 |
| local | glossary_scanned | 10 | 0 |
| local | glossary_approved | 10 | 0 |
| openrouter | translating | 56 | 0 |
| openrouter | refining | 62 | 1 |
| openrouter | formatting | 53 | 0 |
| local | formatting | 3 | 0 |
| openrouter | qa | 10 | 0 |
| openrouter_reasoning | qa | 46 | 0 |
| local | completed | 56 | 0 |
| local | sentinel | 55 | 0 |

## Latest Sentinel Results

Latest scoped Sentinel report for every sampled chapter was clean:

| Chapter | Latest Sentinel | Result |
|---|---|---|
| ch017 | `sentinel_quality_v6-34-m5-dse-treatment-v2_ch017_sentinel_20260701_033515.md` | 0/0/0/0 |
| ch034 | `sentinel_quality_v6-34-m5-dse-treatment-v2_ch034_sentinel_20260701_033516.md` | 0/0/0/0 |
| ch048 | `sentinel_quality_v6-34-m5-dse-treatment-v2_ch048_sentinel_20260701_033517.md` | 0/0/0/0 |
| ch060 | `sentinel_quality_v6-34-m5-dse-treatment-v2_ch060_sentinel_20260701_033517.md` | 0/0/0/0 |
| ch081 | `sentinel_quality_v6-34-m5-dse-treatment-v2_ch081_sentinel_20260701_033518.md` | 0/0/0/0 |
| ch094 | `sentinel_quality_v6-34-m5-dse-treatment-v2_ch094_sentinel_20260701_033519.md` | 0/0/0/0 |
| ch114 | `sentinel_quality_v6-34-m5-dse-treatment-v2_ch114_sentinel_20260701_033520.md` | 0/0/0/0 |
| ch142 | `sentinel_quality_v6-34-m5-dse-treatment-v2_ch142_sentinel_20260701_033521.md` | 0/0/0/0 |
| ch161 | `sentinel_quality_v6-34-m5-dse-treatment-v2_ch161_sentinel_20260701_033522.md` | 0/0/0/0 |
| ch168 | `sentinel_quality_v6-34-m5-dse-treatment-v2_ch168_sentinel_20260701_034515.md` | 0/0/0/0 |

## Interpretation

The DSE treatment slice is valid and clean under current deterministic and Sentinel gates.

Measured improvement:

- The invalid v1 copied-vault problem was eliminated by rebuilding the vault from current production raw/source title sidecars and requiring source parity before provider calls.
- All 10 DSE in-sample chapters completed without current failed blocks.
- Latest scoped Sentinel reports are clean for every sampled chapter.

Remaining limitations:

- This proves DSE treatment can pass in-sample after the source-parity fix; it does not yet prove cross-novel generalization.
- The run still had one recovered OpenRouter empty-assistant failure, so provider smoothness remains a measured risk.
- IRS treatment measurement is still required before moving to out-of-sample Milestone 6.

## Next Action

Continue V6.34 Milestone 5 with IRS treatment measurement in an isolated experiment vault. Do not move to OOS Milestone 6 until IRS treatment produces valid evidence or a documented failure.
