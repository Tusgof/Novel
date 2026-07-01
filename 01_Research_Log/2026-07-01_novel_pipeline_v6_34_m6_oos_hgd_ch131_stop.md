# บันทึกการวิจัย: V6.34 M6 OOS HGD ch131 Stop

## 1. ข้อมูลพื้นฐาน

- Timestamp UTC: `2026-07-01T06:55:23Z`
- โครงการ: Novel Translation Pipeline
- หัวข้อ: V6.34 Milestone 6.2 OOS HGD stop at ch131
- ผู้บันทึก: Codex
- สถานะ: ยกเลิก
- Artifact หลัก:
  - `07_Reports/v6_34_m6_oos_hgd_stop_ch131_glossary_conflict_20260701.md`
  - `Horror Game Developers/04_Work/_experiments/v6_34_m6_hgd_oos_v1/07_Reports/sentinel_quality_v6-34-m6-hgd-oos-v1_ch131_sentinel_20260701_065128.md`

## 2. วัตถุประสงค์

รอบนี้เริ่ม Milestone 6.2 เพื่อวัดว่า treatment จาก in-sample generalize ไปยัง out-of-sample ได้หรือไม่ โดยเริ่มจาก HGD OOS เพราะเป็น single-block chapters และให้ feedback เร็ว

ความสำเร็จของรอบนี้ไม่ใช่การฝืนให้แปลครบ แต่คือการเดินตาม OOS policy: ถ้าเจอ Sentinel blocker/major ต้องหยุดและบันทึกเป็นข้อมูล ห้ามแก้ mid-round โดยไม่มี analysis decision

## 3. วิธีการและขั้นตอน

1. ยืนยันก่อนรันว่า M6.1 scan/glossary gate complete แล้ว และ HGD OOS ไม่มี current failed blocks

2. รัน HGD OOS resume ใน experiment vault

```powershell
cd "D:\Fogust\Workspace\Novel\Horror Game Developers\04_Work\_experiments\v6_34_m6_hgd_oos_v1"
$env:PYTHONIOENCODING='utf-8'
novel-pipeline --config ".system/config.yaml" resume --run-id v6-34-m6-hgd-oos-v1 --manual-action-mode stop
```

3. เมื่อคำสั่ง shell timeout ฝั่งเครื่องมือหลัง 30 นาที ตรวจ process และ status แทนการสั่ง resume ซ้อน

4. หลัง run หยุดที่ Sentinel failure อ่าน ledger record และ Sentinel report โดยตรง

## 4. ผลการศึกษาและข้อมูลดิบ

### Run status at stop

| Metric | Value |
|---|---:|
| Ledger records | 69 |
| Completed HGD OOS chapters | 5 |
| Current failed chapter-level record | 1 |
| Historical failed records | 1 |
| Remaining pending chapters | 5 |

Completed:

- `ch015`
- `ch046`
- `ch060`
- `ch101`
- `ch131`

Pending:

- `ch153`
- `ch184`
- `ch192`
- `ch226`
- `ch262`

### Sentinel finding

| Field | Value |
|---|---|
| Report | `Horror Game Developers/04_Work/_experiments/v6_34_m6_hgd_oos_v1/07_Reports/sentinel_quality_v6-34-m6-hgd-oos-v1_ch131_sentinel_20260701_065128.md` |
| Counts | `0/1/0/0` |
| Severity | major |
| Category | `glossary_coverage_missing` |
| Evidence | `Containment Department -> แผนกกักกัน; glossary=Containment Department.md` |

### Cause evidence

Source contains `Containment Department`, but output used `ภาคส่วนกักกัน`.

Glossary conflict:

| Glossary file | original_term | thai_term | Relevant alias |
|---|---|---|---|
| `Containment Department.md` | `Containment Department` | `แผนกกักกัน` | none |
| `Containment Sector.md` | `Containment Sector` | `ภาคส่วนกักกัน` | `Containment Department` |

การตีความ: นี่เป็น duplicate/alias conflict ใน HGD glossary layer เพราะคำ source เดียวกัน (`Containment Department`) ผูกกับ Thai term ได้สองทาง

## 5. ปัญหา อุปสรรค และการแก้ไข

### Shell command timed out but child process continued

1. What happened: resume command hit the 30-minute tool timeout
2. How it was resolved: checked running processes and status instead of launching a second resume
3. Outcome after resolution: confirmed the original run continued to `ch131` and stopped on Sentinel

### Sentinel stopped on glossary conflict

1. What happened: `ch131` final output used `ภาคส่วนกักกัน` while direct glossary entry requires `แผนกกักกัน`
2. How it was resolved: no repair was applied, because OOS must not be tuned mid-round
3. Outcome after resolution: OOS run is stopped with valid failure evidence for M6.3 analysis

### ข้อจำกัดสำคัญ

- This is not a full OOS result because DSE and IRS OOS translation have not started
- HGD OOS did not finish all 10 chapters
- The failure still provides useful OOS evidence because it identifies a glossary conflict that in-sample treatment did not expose

## 6. ข้อสรุปและก้าวต่อไป

ข้อสรุป: M6.2 stopped validly at HGD `ch131` because OOS exposed a real glossary conflict between `Containment Department` and `Containment Sector`

- This is not a provider failure
- This is not translation truncation
- This is not MoonRead-related
- The likely fix candidate is glossary conflict detection and/or HGD glossary cleanup, but it must be decided in M6.3 analysis rather than patched mid-OOS

ก้าวต่อไป:
1. ทำ M6.3 analysis โดยนับ `ch131` เป็น OOS major glossary conflict
2. ตัดสินว่าควรแก้ Layer 2 HGD glossary only หรือเพิ่ม Layer 0 duplicate-original/alias conflict detector
3. อัปเดต experiment recommendation ก่อน resume OOS รอบถัดไป
