# บันทึกการวิจัย: V6.34 M6 OOS HGD ch184 Stop

## 1. ข้อมูลพื้นฐาน

- Timestamp UTC: `2026-07-01T07:27:52Z`
- โครงการ: Novel Translation Pipeline
- หัวข้อ: V6.34 M6 HGD OOS stop at ch184 QA hard-fail
- ผู้บันทึก: Codex
- สถานะ: ยกเลิก
- Artifact หลัก:
  - `07_Reports/v6_34_m6_oos_hgd_stop_ch184_qa_hard_fail_20260701.md`
  - `Horror Game Developers/04_Work/_experiments/v6_34_m6_hgd_oos_v1/04_Work/ch184/ch184-block-001.qa.json`

## 2. วัตถุประสงค์

รอบนี้ resume HGD OOS หลังจาก treatment ของ `ch131` ผ่านแล้ว เพื่อดูว่า OOS จะเดินต่อได้หรือเจอ failure mode ใหม่

ความสำเร็จของการบันทึกนี้คือระบุจุดหยุดใหม่อย่างตรงไปตรงมา โดยไม่ force-accept และไม่แก้ output ก่อนวิเคราะห์

## 3. วิธีการและขั้นตอน

1. Resume HGD OOS จาก experiment vault หลัง `ch131` treatment commit

```powershell
cd "D:\Fogust\Workspace\Novel\Horror Game Developers\04_Work\_experiments\v6_34_m6_hgd_oos_v1"
$env:PYTHONIOENCODING='utf-8'
novel-pipeline --config ".system/config.yaml" resume --run-id v6-34-m6-hgd-oos-v1 --manual-action-mode stop
```

2. Pipeline completed cached chapters through `ch131`, processed `ch153`, then stopped at `ch184-block-001`
3. Read status and QA artifact for `ch184-block-001`
4. Confirmed no Novel pipeline process remained active; one unrelated Python process belonged to another workspace and was not touched

## 4. ผลการศึกษาและข้อมูลดิบ

### Status at stop

| Metric | Value |
|---|---:|
| Ledger records | 91 |
| Completed HGD OOS chapters | 6 |
| Current failed blocks | 1 |
| Historical failed records | 2 |
| Remaining pending chapters | 3 |

Completed:

- `ch015`
- `ch046`
- `ch060`
- `ch101`
- `ch131`
- `ch153`

Current failed:

- `ch184-block-001`

Pending:

- `ch192`
- `ch226`
- `ch262`

### QA artifact

| Field | Value |
|---|---|
| passed | false |
| retry_count | 2 |
| judge_provider | `openrouter_reasoning` |
| finding 1 | expected term not found: `ปุ่ม Enter` |
| finding 2 | internal thought mistranslation introduced `สะกดรอยตาม` |

## 5. ปัญหา อุปสรรค และการแก้ไข

### QA hard-fail after two retries

1. What happened: `ch184-block-001` failed QA after retry 2
2. How it was resolved: not resolved in this round; stopped according to OOS policy
3. Outcome after resolution: valid OOS failure evidence is recorded for analysis

### Unrelated Python process was visible

1. What happened: process scan showed one Python process after the Novel run stopped
2. How it was resolved: inspected command line and confirmed it belonged to another workspace (`normalize_databento_options.py`)
3. Outcome after resolution: no Novel process was terminated and no unrelated process was touched

## 6. ข้อสรุปและก้าวต่อไป

ข้อสรุป: HGD OOS now exposes a second failure mode at `ch184`: QA catches semantic drift and UI-key glossary handling after normal retries

- This is not the same failure as `ch131`
- The `ch131` treatment worked, but OOS still is not smooth enough for unattended long production
- The next step must be analysis, not manual force-accept

ก้าวต่อไป:
1. Analyze `ch184` source/literal/refined to classify the defect layer
2. Decide whether a prompt/guardrail change is warranted or whether this is run-local recovery
3. Only rerun after the decision is documented
