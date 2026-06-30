# บันทึกการวิจัย: V6.34 M5 HGD Treatment Early Stop

## 1. ข้อมูลพื้นฐาน

- Timestamp UTC: `2026-07-01T00:00:00Z`
- โครงการ: Novel Translation Pipeline
- หัวข้อ: V6.34 M5 HGD treatment early stop
- ผู้บันทึก: Codex
- สถานะ: หยุดอย่างปลอดภัย
- Artifact หลัก:
  - `07_Reports/v6_34_m5_hgd_treatment_early_stop_20260701.md`
  - `Horror Game Developers/04_Work/_experiments/v6_34_m5_hgd_treatment_v1`

## 2. วัตถุประสงค์

รอบนี้ต้องการเริ่ม M5 treatment rerun แบบ isolated เพื่อวัดว่า title/H1 glossary guard และ HGD title map correction ช่วยแก้ปัญหา baseline ได้หรือไม่

ขอบเขตที่รันจริงถูกจำกัดถึง `ch037` แต่ run หยุดก่อนที่ `ch024` เพราะ Sentinel พบ blocker

## 3. วิธีการและขั้นตอน

1. สร้าง treatment vault ใหม่จาก baseline vault แล้วล้าง `04_Work`, `05_Output`, และ `06_Logs`
2. รัน preflight ใน treatment vault
3. รัน scan-only สำหรับ HGD in-sample 10 ตอน
4. Commit `glossary_approved` แบบ hold-all เพื่อไม่เปลี่ยนตัวแปร glossary ระหว่าง comparison
5. Resume แบบ bounded ถึง `ch037`
6. หยุดเมื่อ Sentinel block `ch024`

## 4. ผลการศึกษาและข้อมูลดิบ

| Item | Result |
|---|---|
| Treatment vault preflight | ready |
| Scan-only candidates | 26 |
| Glossary approval | 10/10 chapter-level `glossary_approved` |
| Completed block | `ch024-block-001` |
| Current failed item | `ch024` Sentinel gate |
| Sentinel count | blocker/major/minor/info `3/0/0/0` |
| Production output/MoonRead | unchanged |

Sentinel blocker ทั้ง 3 รายการเป็น approved glossary English leakage:

- `The Nightwalker -> นักเดินราตรี`
- `Field Agent -> เจ้าหน้าที่ภาคสนาม`
- `Nightwalker -> นักเดินราตรี`

## 5. ปัญหา อุปสรรค และการแก้ไข

ระหว่าง run พบ HGD title map gap เพิ่มเติม: `The missing piece` ยังไม่มี runtime mapping ใน `HGD_TITLE_MAP` แม้ historical repair script เคยมีคำแปลนี้แล้ว

การแก้ที่ทำแล้ว:

- เพิ่ม `The missing piece -> ชิ้นส่วนที่หายไป` ใน runtime title map
- sync HGD title normalizer script
- รัน compile และ test suite ผ่าน

ยังไม่ได้แก้ output `ch024` เพราะรอบนี้ต้องเก็บเป็น experiment evidence ไม่ใช่ production patch

## 6. ข้อสรุปและก้าวต่อไป

M5 treatment run ให้ข้อมูลสำคัญเพิ่ม:

- title/H1 path ดีขึ้นพอให้ `ch024` assemble ได้
- Sentinel ยังจับ approved glossary English parenthetical leakage ได้ถูกต้อง
- defect ถัดไปควรถูกวิเคราะห์เป็น treatment เพิ่ม: deterministic cleanup, formatting prompt constraint, หรือ rerun recovery

ก้าวต่อไปคือเลือก treatment สำหรับ approved glossary parenthetical leakage แล้ว rerun จาก stage ที่ปลอดภัยใน treatment vault
