# V6.34 M6 IRS OOS Completion Report

## Scope

- Novel: Infinite Regressor Stories
- Experiment vault: `Infinite Regressor Stories/04_Work/_experiments/v6_34_m6_irs_oos_v1`
- Run ID: `v6-34-m6-irs-oos-v1`
- Locked OOS chapters: `ch012`, `ch053`, `ch095`, `ch144`, `ch187`, `ch208`, `ch258`, `ch290`, `ch323`, `ch372`
- Production impact: none. Output remains experiment-only and was not published to MoonRead.

## Result

IRS OOS completed validly.

- Completed blocks: `33/33`
- Completed chapters: `10/10`
- Current failed blocks: none
- Manual actions needed: none
- Final experiment outputs: exist for all 10 chapters
- Source parity against production raw: `0` mismatches
- Deterministic experiment-output checks: passed
- Runtime Sentinel: completed for all 10 chapters; latest reports show `0/0/0/0`

## Verification

Commands run:

```powershell
cd "D:\Fogust\Workspace\Novel\Infinite Regressor Stories\04_Work\_experiments\v6_34_m6_irs_oos_v1"
$env:PYTHONIOENCODING='utf-8'
novel-pipeline --config ".system/config.yaml" status --run-id v6-34-m6-irs-oos-v1
```

Status summary:

- Records: `221`
- Current failed blocks: none
- Historical failed records: `2`
- Output exists for each locked chapter.
- Manual actions needed: none

```powershell
cd "D:\Fogust\Workspace\Novel"
$env:PYTHONIOENCODING='utf-8'
python scripts\verify_experiment_source_parity.py --novel-root "Infinite Regressor Stories" --experiment-root "Infinite Regressor Stories\04_Work\_experiments\v6_34_m6_irs_oos_v1" --chapters "ch012,ch053,ch095,ch144,ch187,ch208,ch258,ch290,ch323,ch372"
```

Source parity result:

- Checked chapters: `10`
- Mismatches: `0`

Experiment-output guardrail check:

- Checked chapters: `10`
- Issues: `0`
- Checks covered: missing outputs, Han/CJK body leakage, Thai numeral leakage by codepoint, provider/meta leakage, quote-only lines, title-like body paragraphs, and paragraphs over 900 characters.

Sentinel evidence:

- `Infinite Regressor Stories/04_Work/_experiments/v6_34_m6_irs_oos_v1/07_Reports/sentinel_quality_v6-34-m6-irs-oos-v1_ch012_sentinel_20260701_124446.md`
- `Infinite Regressor Stories/04_Work/_experiments/v6_34_m6_irs_oos_v1/07_Reports/sentinel_quality_v6-34-m6-irs-oos-v1_ch053_sentinel_20260701_125235.md`
- `Infinite Regressor Stories/04_Work/_experiments/v6_34_m6_irs_oos_v1/07_Reports/sentinel_quality_v6-34-m6-irs-oos-v1_ch095_sentinel_20260701_125829.md`
- `Infinite Regressor Stories/04_Work/_experiments/v6_34_m6_irs_oos_v1/07_Reports/sentinel_quality_v6-34-m6-irs-oos-v1_ch144_sentinel_20260701_130815.md`
- `Infinite Regressor Stories/04_Work/_experiments/v6_34_m6_irs_oos_v1/07_Reports/sentinel_quality_v6-34-m6-irs-oos-v1_ch187_sentinel_20260701_131453.md`
- `Infinite Regressor Stories/04_Work/_experiments/v6_34_m6_irs_oos_v1/07_Reports/sentinel_quality_v6-34-m6-irs-oos-v1_ch208_sentinel_20260701_132143.md`
- `Infinite Regressor Stories/04_Work/_experiments/v6_34_m6_irs_oos_v1/07_Reports/sentinel_quality_v6-34-m6-irs-oos-v1_ch258_sentinel_20260701_133038.md`
- `Infinite Regressor Stories/04_Work/_experiments/v6_34_m6_irs_oos_v1/07_Reports/sentinel_quality_v6-34-m6-irs-oos-v1_ch290_sentinel_20260701_133755.md`
- `Infinite Regressor Stories/04_Work/_experiments/v6_34_m6_irs_oos_v1/07_Reports/sentinel_quality_v6-34-m6-irs-oos-v1_ch323_sentinel_20260701_134603.md`
- `Infinite Regressor Stories/04_Work/_experiments/v6_34_m6_irs_oos_v1/07_Reports/sentinel_quality_v6-34-m6-irs-oos-v1_ch372_sentinel_20260701_135244.md`

Each latest scoped Sentinel report is safe to publish within the experiment surface and reports blocker/major/minor/info `0/0/0/0`.

## Provider And Smoothness Evidence

Provider/stage counts from the run ledger:

| Stage | Provider / model | Count |
|---|---:|---:|
| translating completed | openrouter | 33 |
| refining completed | openrouter | 45 |
| refining failed | openrouter `deepseek/deepseek-v4-flash` | 2 |
| refining completed | local_recovery | 2 |
| qa completed | openrouter `deepseek/deepseek-v4-flash` | 30 |
| qa completed | openrouter `google/gemini-3-flash-preview` | 3 |
| formatting completed | openrouter `deepseek/deepseek-v4-flash` | 22 |
| formatting completed | openrouter `google/gemini-3-flash-preview` | 7 |
| formatting completed | local | 4 |
| sentinel completed | local | 10 |

Historical failed records:

1. `ch208-block-002` refining failed because OpenRouter returned an empty assistant message after 39.50 seconds. The pipeline recovered and completed the block.
2. `ch290-block-002` refining failed because OpenRouter returned an empty assistant message after 38.64 seconds. The pipeline recovered and completed the block.

Interpretation:

- Product-surface quality improved versus earlier IRS treatment: no Sentinel blocker/major/minor/info findings remained in this OOS slice.
- Long-run smoothness is still imperfect. The OOS run required retries/fallbacks and produced 2 historical provider failures.
- IRS OOS did not repeat the previous CJK/Hanja parenthetical hard-fail or the `Complete Memory` minor miss.

## Next Action

Proceed to V6.34 M6 cross-novel OOS comparison across HGD, DSE, and IRS. Do not publish experiment outputs to MoonRead. Production recommendation should account for smoothness risk, not only final output quality.
