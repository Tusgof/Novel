# V6.34 M5 HGD Baseline vs Treatment Comparison

Date: 2026-07-01

## Scope

This report compares the V6.34 HGD in-sample baseline run against the HGD treatment run.

- Baseline run ID: `v6-34-m3-hgd-baseline-v1`
- Treatment run ID: `v6-34-m5-hgd-treatment-v1`
- Sampled HGD in-sample chapters: `ch024`, `ch037`, `ch066`, `ch103`, `ch132`, `ch142`, `ch170`, `ch196`, `ch225`, `ch250`
- Output scope: isolated experiment vaults only
- MoonRead publication: none

## Metric Summary

| Metric | Baseline | Treatment | Movement |
|---|---:|---:|---|
| Planned HGD in-sample chapters | 10 | 10 | unchanged |
| Completed chapters before valid stop/final status | 2 | 10 | improved |
| Current failed blocks/chapters | 1 (`ch037` Sentinel) | 0 | improved |
| Latest Sentinel blocker/major/minor/info for compared stop point | `0/2/0/0` on `ch037` | `0/0/0/0` on `ch037` | improved |
| Latest Sentinel all completed HGD treatment chapters | not applicable; baseline stopped early | `0/0/0/0` for all 10 | improved |
| Historical failed records | 1 | 6 | worse operational smoothness |
| QA hard-fail records | 0 | 2 | worse operational smoothness |
| QA omission literal-safe recoveries | not observed before stop | 5 chapters | unresolved risk |
| Production/MoonRead mutation | 0 | 0 | unchanged/pass |

## Baseline Evidence

Baseline completed `ch024` and `ch037`, then stopped at a valid Sentinel gate:

- `novel-pipeline status`: 44 ledger records, completed blocks `ch024-block-001` and `ch037-block-001`, current failed chapter `ch037`.
- Sentinel report: `Horror Game Developers/04_Work/_experiments/v6_34_m3_hgd_baseline_v1/07_Reports/sentinel_quality_manual_experiment_ch037_probe_20260630_224633.md`
- Sentinel result for `ch037`: `0/2/0/0`
- Findings:
  - `Velora Art Museum -> พิพิธภัณฑ์ศิลปะเวโลรา` missing from final output.
  - `Art Museum -> พิพิธภัณฑ์ศิลปะเวโลรา` missing from final output.

The baseline stop is useful data because it exposed a final title/H1 glossary drift that provider QA did not catch.

## Treatment Evidence

Treatment completed all 10 HGD in-sample chapters:

- `novel-pipeline status`: 169 ledger records, 10/10 completed blocks, current failed blocks none.
- Latest scoped Sentinel for every treatment chapter: `0/0/0/0`.
- Treatment output remained isolated in `Horror Game Developers/04_Work/_experiments/v6_34_m5_hgd_treatment_v1`.
- No production `05_Output` or MoonRead publication was made from this experiment output.

Treatment effects observed:

| Defect Class | Evidence | Treatment Outcome |
|---|---|---|
| Title/H1 glossary drift | baseline `ch037` missed `Velora Art Museum` / `Art Museum` approved Thai term | title/H1 glossary validation and HGD title map correction; `ch037` Sentinel `0/0/0/0` |
| Approved glossary English parenthetical leakage | treatment initially stopped on `ch024` with `The Nightwalker`, `Nightwalker`, `Field Agent` leakage | deterministic approved-glossary parenthetical cleanup; `ch024` Sentinel `0/0/0/0` |
| BOM-prefixed glossary notes skipped | `ch132` parser skipped HGD glossary notes with UTF-8 BOM | parser tolerates BOM; `ch132` Sentinel `0/0/0/0` |
| HGD loose glossary variants | `ch132` used `ซาร่าห์`, `แผนกสะสม`, `แผนกจัดเก็บ` | rejected variants recorded in HGD glossary notes |
| Redacted rank hallucination | `ch250` translated source `-ranked Gate` as `เกตระดับ S` | redacted-rank guard repairs to `เกตไม่ระบุแรงก์` only when source lacks explicit S-rank |

## Operational Caveats

Treatment improved the measured output surface, but it did not yet prove unattended long-run smoothness:

- Historical failed records increased from `1` in baseline to `6` in treatment because the treatment run progressed farther and hit more gates.
- QA hard-fail records appeared in treatment: `ch132-block-001` and `ch250-block-001`.
- QA omission literal-safe recovery was needed for 5 chapters: `ch024`, `ch066`, `ch142`, `ch170`, `ch196`.
- Formatting and QA fallback paths were exercised, including `ch225` QA via `qwen` fallback.

These are not failures of the treatment hypothesis, but they are evidence that the pipeline still needs cross-novel measurement before production scaling.

## Decision

The HGD treatment improved measured Sentinel/product-surface outcomes enough to continue V6.34 M5, but only as experiment work.

Next bounded step:

1. Continue treatment measurement on DSE in-sample chapters in an isolated experiment vault.
2. Then continue treatment measurement on IRS in-sample chapters in an isolated experiment vault.
3. Do not publish any experiment output.
4. Stop on Sentinel blocker/major, provider failure, manual QA prompt, source mismatch, validation failure, or unexpected scope expansion.
5. After DSE/IRS treatment data exists, compare cross-novel results before running out-of-sample M6.

## Verification Commands Used

```powershell
novel-pipeline --config ".system/config.yaml" status --run-id v6-34-m3-hgd-baseline-v1
novel-pipeline --config ".system/config.yaml" status --run-id v6-34-m5-hgd-treatment-v1
```

