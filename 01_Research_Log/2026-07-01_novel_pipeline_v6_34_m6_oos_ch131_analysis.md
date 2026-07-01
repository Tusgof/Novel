# บันทึกการวิจัย: V6.34 M6.3 OOS ch131 Analysis

## 1. ข้อมูลพื้นฐาน

- Timestamp UTC: `2026-07-01T06:58:49Z`
- โครงการ: Novel Translation Pipeline
- หัวข้อ: V6.34 M6.3 analysis for HGD ch131 OOS glossary conflict
- ผู้บันทึก: Codex
- สถานะ: เสร็จสิ้น
- Artifact หลัก:
  - `07_Reports/v6_34_m6_oos_ch131_analysis_treatment_selection_20260701.md`
  - `Horror Game Developers/04_Work/_experiments/v6_34_m6_hgd_oos_v1/07_Reports/v6_34_m6_hgd_oos_glossary_conflicts_after_ch131_stop.md`

## 2. วัตถุประสงค์

รอบนี้ต้องวิเคราะห์ OOS failure จาก HGD `ch131` ก่อนแก้ เพื่อแยกว่าเป็นปัญหาระดับ multi-novel, language, novel-specific, run-local, หรือ MoonRead

เป้าหมายคือเลือก treatment ที่มีหลักฐานรองรับและไม่ลดคุณภาพงานแปล โดยยังรักษาหลัก OOS ว่าไม่แก้แบบ ad hoc ระหว่างรันโดยไม่มี analysis decision

## 3. วิธีการและขั้นตอน

1. อ่าน Sentinel report จาก HGD OOS `ch131`
2. ตรวจ source raw และ final output เพื่อยืนยัน source term กับ output term
3. ตรวจ glossary notes ที่เกี่ยวข้อง:
   - `Containment Department.md`
   - `Containment Sector.md`
4. รัน glossary conflicts report ใน experiment vault

```powershell
novel-pipeline --config ".system/config.yaml" report glossary-conflicts --run-id v6-34-m6-hgd-oos-v1 --output "07_Reports/v6_34_m6_hgd_oos_glossary_conflicts_after_ch131_stop.md"
```

5. จำแนก defect ตาม layer และเลือก treatment ที่ควรทำก่อน resume OOS

## 4. ผลการศึกษาและข้อมูลดิบ

### Defect classification

| Layer | Result |
|---|---|
| Layer 0 multi-novel | มี detector gap: original/alias collision ยังไม่ถูก flag เป็นชนิดชัดเจน |
| Layer 1 language | ไม่เกี่ยว |
| Layer 2 novel-specific | HGD glossary มี conflict จริง |
| Layer 3 run-local | ไม่ใช่ artifact patch เฉพาะตอน |
| Layer 4 MoonRead | ไม่เกี่ยว เพราะเป็น experiment vault |

### Glossary conflict

| Glossary file | original_term | thai_term | Conflicting surface |
|---|---|---|---|
| `Containment Department.md` | `Containment Department` | `แผนกกักกัน` | direct original |
| `Containment Sector.md` | `Containment Sector` | `ภาคส่วนกักกัน` | alias: `Containment Department` |

### Existing detector behavior

`glossary-conflicts` already produced an actionable report, but it did not identify this exact original-vs-alias collision. It listed nearby overlap classes, while the failure escaped until Sentinel checked final output.

## 5. ปัญหา อุปสรรค และการแก้ไข

### Existing glossary conflict report is not specific enough

1. What happened: `Containment Department` conflict was not reported as its own source-surface collision
2. How it was resolved: no code change in this analysis step; selected treatment is to extend the detector
3. Outcome after resolution: M6.3 has a clear Layer 0 + Layer 2 treatment plan

### HGD glossary contains old alias policy

1. What happened: older `Containment Sector.md` aliases include `Containment Department`, but later HGD glossary added a direct `Containment Department.md` with another Thai term
2. How it was resolved: no glossary edit in this analysis step; selected treatment is to remove only the conflicting aliases
3. Outcome after resolution: next implementation step is bounded and testable

## 6. ข้อสรุปและก้าวต่อไป

ข้อสรุป: HGD `ch131` OOS failure should be treated as a glossary-system defect, not a one-off translation mistake

- Layer 0 needs a detector for approved original/alias source-surface collisions
- Layer 2 HGD needs `Containment Sector.md` alias cleanup
- Run-local output patching is not appropriate before policy fix

ก้าวต่อไป:
1. Implement source-surface collision detection in `build_glossary_conflicts_report()`
2. Add regression test for original/alias collision with different Thai terms
3. Remove conflicting HGD aliases from `Containment Sector.md`
4. Rerun the HGD OOS affected slice only after these treatment changes pass validation
