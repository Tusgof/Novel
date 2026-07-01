# บันทึกการวิจัย: V6.34 M6 HGD OOS หยุดที่ ch192 จากสรรพนาม peer dialogue

## 1. ข้อมูลพื้นฐาน

- Timestamp UTC: `2026-07-01T08:02:04Z`
- โครงการ: Novel Translation Pipeline
- หัวข้อ: V6.34 M6 HGD OOS ch192 QA hard-fail
- ผู้บันทึก: Codex
- สถานะ: อยู่ระหว่างดำเนินการ
- Artifact หลัก:
  - `07_Reports/v6_34_m6_oos_hgd_stop_ch192_pronoun_drift_20260701.md`
  - `Horror Game Developers/04_Work/_experiments/v6_34_m6_hgd_oos_v1/04_Work/ch192/ch192-block-001.qa.json`
  - `Horror Game Developers/04_Work/_experiments/v6_34_m6_hgd_oos_v1/04_Work/ch192/ch192-block-001.refined.json`

## 2. วัตถุประสงค์

รอบนี้มีเป้าหมายเพื่อ resume HGD out-of-sample slice ของ V6.34 หลังแก้ `ch184` แล้ววัดว่าทreatment ก่อนหน้า generalize ต่อได้หรือไม่ โดยยังคงกฎเดิมว่า OOS output เป็นงานทดลองเท่านั้นและต้องหยุดเมื่อเจอ QA hard-fail, Sentinel blocker/major, provider failure, หรือ scope expansion

ความสำเร็จของรอบนี้คือ HGD OOS สามารถเดินต่อจาก `ch192` ไปจนจบ sample ได้โดยไม่มี blocker ใหม่ หรือถ้าหยุด ต้องบันทึก failure เป็นข้อมูลทดลองก่อนแก้ไข

## 3. วิธีการและขั้นตอน

1. ตรวจสถานะก่อน resume และยืนยันว่า run ไม่มี current failed blocks หลัง `ch184`

```powershell
cd "D:\Fogust\Workspace\Novel\Horror Game Developers\04_Work\_experiments\v6_34_m6_hgd_oos_v1"
$env:PYTHONIOENCODING='utf-8'
novel-pipeline --config ".system/config.yaml" status --run-id v6-34-m6-hgd-oos-v1
```

2. Resume แบบหยุดเมื่อเจอ manual action

```powershell
novel-pipeline --config ".system/config.yaml" resume --run-id v6-34-m6-hgd-oos-v1 --manual-action-mode stop
```

3. หลัง run หยุด อ่าน status และ artifact ของ `ch192-block-001`

```powershell
novel-pipeline --config ".system/config.yaml" status --run-id v6-34-m6-hgd-oos-v1
```

## 4. ผลการศึกษาและข้อมูลดิบ

### ผลลัพธ์หลัก

| Metric | Value |
|---|---:|
| Exit code | `1` |
| Completed HGD OOS chapters after stop | `7/10` |
| Current failed blocks | `1` |
| Failed block | `ch192-block-001` |
| QA retry count | `2` |
| Historical failed records | `4` |

### สถานะ chapter

| Chapter | Status |
|---|---|
| `ch015` | complete |
| `ch046` | complete |
| `ch060` | complete |
| `ch101` | complete |
| `ch131` | complete after treatment |
| `ch153` | complete |
| `ch184` | complete after treatment |
| `ch192` | failed at QA |
| `ch226` | pending translating |
| `ch262` | pending translating |

### QA failure

QA feedback:

> FAIL: Peer address uses คุณ instead of preferred นาย for casual peer dialogue, violating pronoun drift rule.

The refined text contains six `คุณ` occurrences. The directly relevant peer-dialogue examples include:

- `"ถ้าคุณมีอุปกรณ์อิเล็กทรอนิกส์อะไร ดีที่สุดคือปิดมันซะ"`
- `"...คุณรู้อะไรบางอย่างแล้วใช่ไหม?"`
- `"คุณฉลาดไม่เบาเลยนะ"`
- `"มิน่าล่ะ หัวหน้าแผนก ถึงได้ชอบคุณนัก"`

## 5. ปัญหา อุปสรรค และการแก้ไข

ปัญหา:

1. HGD OOS stopped at `ch192-block-001` because QA judged peer-dialogue address as pronoun drift.
2. The pipeline behaved correctly by stopping instead of force-accepting the hard-fail.
3. No repair was applied in this log. This preserves the failure as OOS evidence before analysis.

ข้อจำกัดสำคัญ:

- This log does not yet prove whether the issue is Layer 2 HGD-specific pronoun policy weakness or a reusable Layer 0 enforcement gap.
- Sentinel did not run for `ch192` because the block stopped before formatting/final assembly.

## 6. ข้อสรุปและก้าวต่อไป

ข้อสรุป: HGD OOS treatment has not yet proven smooth long-run generalization because `ch192` introduced a new QA hard-fail around pronoun consistency.

- The failure is quality-related, not provider outage.
- The stop is useful evidence for the V6.34 objective: consistency and sustainable long-run execution.
- The next step must be analysis before rerun, not immediate patching.

ก้าวต่อไป:

1. Analyze `ch192-block-001` source/literal/refined text around the `คุณ` lines.
2. Classify the defect layer: run-local, HGD novel-specific, or reusable multi-novel pronoun enforcement.
3. Select the smallest treatment and verification method.
4. Rerun from the earliest safe stage only after the treatment decision is recorded.

