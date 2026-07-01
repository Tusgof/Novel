# V6.34 M5 IRS Treatment Stop - ch020

Date: 2026-07-01

## Scope

- Novel: Infinite Regressor Stories
- Experiment vault: `Infinite Regressor Stories/04_Work/_experiments/v6_34_m5_irs_treatment_v1`
- Run ID: `v6-34-m5-irs-treatment-v1`
- Chapter: `ch020`
- Status: stopped at Sentinel blocker after `ch020`
- Production/MoonRead impact: none

## What Completed

- Source parity before provider calls: `Checked 10 chapters`, `Mismatches: 0`
- Scan-only gate completed for the official IRS M3/M5 sample:
  - `ch020,ch067,ch080,ch119,ch160,ch207,ch261,ch276,ch322,ch361`
  - New candidates: 119
- Treatment glossary decision: hold/reject all 119 new candidates for measurement, approve no new terms
- `glossary_approved` records committed for 10/10 experiment chapters
- `ch020` translated/refined/QA/formatted/assembled:
  - Blocks complete: 4/4
  - Current failed blocks: none
  - Historical failed records: none

## Stop Condition

Manual Sentinel was run for `ch020` after enabling experiment-local Sentinel config:

```powershell
python scripts\sentinel_quality_report.py --scope v6-34-m5-irs-treatment-v1_ch020_manual_sentinel --novel infinite-regressor-stories --chapters ch020 --fail-on major --skip-advisory-english
```

Result:

- Report: `Infinite Regressor Stories/04_Work/_experiments/v6_34_m5_irs_treatment_v1/07_Reports/sentinel_quality_v6-34-m5-irs-treatment-v1_ch020_manual_sentinel_20260701_040809.md`
- Safe to publish: no
- Blocker/Major/Minor/Info: `1/0/0/0`

Finding:

- `glossary_note_leakage`: final output contains glossary/category note text.
- Evidence: `ดังซอริน: ชื่อตัวละคร`

## Root Cause

The source chapter ends with an empty source marker:

```text
Footnotes:
```

There are no real source footnote entries after that marker. During translation/refinement, the model filled the empty footnote section with glossary/category metadata:

```text
เชิงอรรถ:
การร่ายเพลงสาป: ความสามารถ
ดังซอริน: ชื่อตัวละคร
หัวหน้ากิลด์: ตำแหน่ง
สิบขา: สิ่งมีชีวิต/ศัตรู
สัปเหร่อ: ตำแหน่ง/ฉายา
ผู้ย้อนกลับ: คำเรียกผู้ที่ย้อนเวลากลับมาได้
```

This appears in `ch020-block-004.literal.json`, persists into `ch020-block-004.refined.json`, and reaches final output.

Layer classification:

- Layer 1 language/source-shape risk: English source chapters can contain empty `Footnotes:` markers.
- Layer 2 IRS novel risk: IRS uses glossary-heavy English source with frequent author/source markers, making metadata hallucination more likely.
- Layer 0 prevention candidate: output guardrail/Sentinel should reject glossary/category note leakage for all novels; this part already worked and stopped the run.

## Interpretation

The treatment run is not ready to continue blindly. Sentinel correctly blocked the final product surface, but runtime Sentinel was initially missing from the copied IRS experiment config, so `ch020` needed a manual Sentinel run.

The next treatment step should add a low-risk source/output prevention before resuming:

1. Strip or neutralize empty trailing `Footnotes:` source markers before provider prompts, or explicitly instruct providers not to invent footnotes.
2. Ensure IRS experiment/production config includes blocking Sentinel before translation starts.
3. Add/confirm deterministic guardrail coverage for Thai glossary category leakage after `เชิงอรรถ:`.
4. Rerun `ch020` from the earliest affected stage after the prevention is implemented, then rerun Sentinel.

## Next Action

Do not continue to `ch067` yet. First implement the smallest prevention for empty source footnote marker leakage and experiment Sentinel config parity, then rerun `ch020` in the treatment vault and compare metrics.
