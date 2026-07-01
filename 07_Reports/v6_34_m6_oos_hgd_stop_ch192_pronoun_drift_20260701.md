# V6.34 M6 OOS HGD Stop: ch192 Pronoun Drift

Date: 2026-07-01

## Summary

V6.34 Milestone 6.2 HGD out-of-sample translation resumed from `ch192` and stopped safely at `ch192-block-001` during QA escalation.

This is experiment evidence only. No production output, MoonRead content, production glossary, or production ledger was modified.

## Command

```powershell
cd "D:\Fogust\Workspace\Novel\Horror Game Developers\04_Work\_experiments\v6_34_m6_hgd_oos_v1"
$env:PYTHONIOENCODING='utf-8'
novel-pipeline --config ".system/config.yaml" resume --run-id v6-34-m6-hgd-oos-v1 --manual-action-mode stop
```

Exit code: `1`

## Stop Point

- Run ID: `v6-34-m6-hgd-oos-v1`
- Chapter: `ch192`
- Block: `ch192-block-001`
- Stage: `qa`
- QA provider: `openrouter_reasoning`
- Retry count: `2`
- Current failed block: `ch192-block-001`

QA feedback:

> FAIL: Peer address uses คุณ instead of preferred นาย for casual peer dialogue, violating pronoun drift rule.

## Current Run State After Stop

- Completed OOS HGD chapters: `ch015`, `ch046`, `ch060`, `ch101`, `ch131`, `ch153`, `ch184`
- Failed/current blocker: `ch192-block-001`
- Pending chapters: `ch226`, `ch262`
- Final output missing for `ch192`
- No `ch024+` scope issue beyond the locked OOS sample

Status command reported:

- Records: `117`
- Current failed blocks: `ch192-block-001`
- Historical failed records: `4`
- Manual actions needed: inspect failed blocks and rerun from appropriate stage

## Evidence

QA artifact:

`Horror Game Developers/04_Work/_experiments/v6_34_m6_hgd_oos_v1/04_Work/ch192/ch192-block-001.qa.json`

Refined artifact:

`Horror Game Developers/04_Work/_experiments/v6_34_m6_hgd_oos_v1/04_Work/ch192/ch192-block-001.refined.json`

The refined text contains six `คุณ` occurrences. The QA-relevant peer-dialogue examples include:

- `"ถ้าคุณมีอุปกรณ์อิเล็กทรอนิกส์อะไร ดีที่สุดคือปิดมันซะ"`
- `"...คุณรู้อะไรบางอย่างแล้วใช่ไหม?"`
- `"คุณฉลาดไม่เบาเลยนะ"`
- `"มิน่าล่ะ หัวหน้าแผนก ถึงได้ชอบคุณนัก"`

## Preliminary Classification

- Layer: likely Layer 2 novel-specific HGD dialogue/pronoun policy, with possible Layer 0 opportunity if pronoun-policy enforcement can be made generic without hurting other novels.
- Failure type: QA hard-fail / pronoun drift.
- Provider outage: none observed.
- Glossary collision: none observed in this stop.
- Sentinel blocker/major: not reached because QA stopped before formatting/final assembly.

## Next Safe Action

Analyze `ch192-block-001` before any rerun:

1. Compare source/literal/refined text around the `คุณ` lines.
2. Decide whether this is a run-local repair, HGD prompt/profile weakness, or a reusable pronoun-policy enforcement gap.
3. Only then rerun from the earliest safe stage, likely `refine` if the source/literal are intact.

