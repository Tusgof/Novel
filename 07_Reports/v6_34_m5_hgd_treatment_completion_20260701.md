# V6.34 M5 HGD Treatment Completion

Date: 2026-07-01
Run ID: `v6-34-m5-hgd-treatment-v1`
Experiment vault: `Horror Game Developers/04_Work/_experiments/v6_34_m5_hgd_treatment_v1`

## Summary

The HGD treatment slice for V6.34 M5 completed all 10 in-sample chapters in the isolated experiment vault.

Completed chapters:

- `ch024`
- `ch037`
- `ch066`
- `ch103`
- `ch132`
- `ch142`
- `ch170`
- `ch196`
- `ch225`
- `ch250`

Current failed blocks: none.

No experiment output was published to MoonRead.

## Sentinel Results

| Chapter | Latest Sentinel | Result |
|---|---|---|
| `ch024` | `sentinel_quality_v6-34-m5-hgd-treatment-v1_ch024_sentinel_20260701_003142.md` | `0/0/0/0` |
| `ch037` | `sentinel_quality_v6-34-m5-hgd-treatment-v1_ch037_sentinel_20260701_003143.md` | `0/0/0/0` |
| `ch066` | `sentinel_quality_v6-34-m5-hgd-treatment-v1_ch066_sentinel_20260701_003144.md` | `0/0/0/0` |
| `ch103` | `sentinel_quality_v6-34-m5-hgd-treatment-v1_ch103_sentinel_20260701_003145.md` | `0/0/0/0` |
| `ch132` | `sentinel_quality_v6-34-m5-hgd-treatment-v1_ch132_sentinel_20260701_003146.md` | `0/0/0/0` |
| `ch142` | `sentinel_quality_v6-34-m5-hgd-treatment-v1_ch142_sentinel_20260701_003147.md` | `0/0/0/0` |
| `ch170` | `sentinel_quality_v6-34-m5-hgd-treatment-v1_ch170_sentinel_20260701_003148.md` | `0/0/0/0` |
| `ch196` | `sentinel_quality_v6-34-m5-hgd-treatment-v1_ch196_sentinel_20260701_003149.md` | `0/0/0/0` |
| `ch225` | `sentinel_quality_v6-34-m5-hgd-treatment-v1_ch225_sentinel_20260701_003150.md` | `0/0/0/0` |
| `ch250` | `sentinel_quality_v6-34-m5-hgd-treatment-v1_ch250_sentinel_20260701_004801.md` | `0/0/0/0` |

## Observed Treatment Effects

| Issue Class | Evidence | Treatment / Outcome |
|---|---|---|
| Title/H1 glossary drift | baseline stopped at `ch037` on `Velora Art Museum` | title/H1 glossary validation and HGD title map correction; `ch037` passes Sentinel |
| Approved English parenthetical leakage | treatment initially blocked at `ch024` | deterministic parenthetical cleanup; `ch024` passes Sentinel |
| BOM-prefixed glossary notes skipped | `ch132` parser skipped Sarah/department notes | BOM-tolerant glossary parser; `ch132` passes Sentinel |
| HGD loose glossary variants | `ch132` used `ซาร่าห์`, `แผนกสะสม`, `แผนกจัดเก็บ` | rejected variants added to HGD glossary notes |
| Redacted rank hallucination | `ch250` translated source `-ranked Gate` as `เกตระดับ S` | redacted-ranked-gate repair changed it to `เกตไม่ระบุแรงก์`; `ch250` passes QA/Sentinel |

## Recovery / Retry Notes

QA omission literal-safe recovery was needed for:

- `ch024`
- `ch066`
- `ch142`
- `ch170`
- `ch196`

Other notable routing:

- `ch225` QA completed through `qwen` fallback.
- `ch250` required rerun from `translating` after adding the redacted-rank repair.
- Formatting fallback occurred historically in the run, but all final HGD treatment outputs passed scoped Sentinel.

## Verification

- `python -m compileall novel_pipeline`: passed
- `python test_translation.py`: passed
- `novel-pipeline --config ".system/config.yaml" status --run-id v6-34-m5-hgd-treatment-v1`: 10/10 blocks complete, current failed blocks none
- Latest scoped Sentinel for all 10 HGD treatment chapters: `0/0/0/0`

## Next Step

Do not publish experiment output. Compare HGD baseline-versus-treatment metrics and decide the next bounded V6.34 step: continue treatment measurement for DSE/IRS in-sample chapters or revise the treatment set first.
