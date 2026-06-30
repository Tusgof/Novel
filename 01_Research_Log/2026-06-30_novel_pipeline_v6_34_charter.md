# บันทึกการวิจัย: กรอบการทดลอง V6.34 Libra - Pilot แบบข้ามนิยาย

## 1. ข้อมูลพื้นฐาน

- Timestamp UTC: `2026-06-30T22:11:47Z`
- โครงการ: Novel Translation Pipeline
- หัวข้อ: V6.34 Libra - Pilot research charter
- ผู้บันทึก: Codex
- สถานะ: เสร็จสิ้น
- Artifact หลัก:
  - `IMPLEMENT_PLAN.md`
  - `Backup_IMPLEMENT_PLAN/01072026_IMPLEMENT_PLAN.md`

## 2. วัตถุประสงค์

รอบนี้มีเป้าหมายเพื่อเปลี่ยน V6.34 จากงานทดลองที่เริ่มจาก IRS เป็นงานวิจัยข้ามนิยายที่วัดผลได้จริง โดยยึดคำตอบล่าสุดของผู้ใช้ว่า Libra - Pilot ไม่ได้มีหน้าที่พิสูจน์แบบผ่าน/ไม่ผ่านเพียงอย่างเดียว แต่ต้องใช้เพื่อเพิ่มประสิทธิภาพของ pipeline ทั้งระบบ ลดข้อผิดพลาด และสร้างหลักฐานว่าการปรับเปลี่ยนตามสมมติฐานทำให้ผลลัพธ์ดีขึ้นจริง

ความสำเร็จของรอบนี้คือมีแผนทดลองที่ชัดเจนว่า sample ต้องมาจาก raw source ของ DSE, HGD, และ IRS ทั้งสามเรื่อง ต้องทำ baseline ให้จบหนึ่งรอบก่อนแก้ ต้องแยกว่าปัญหาเป็น multi-novel หรือ novel-specific และต้องเก็บ output ของการทดลองไว้เป็น experiment output เท่านั้น ไม่ใช่งานสำหรับ publish เข้า MoonRead

## 3. วิธีการและขั้นตอน

1. อ่านสถานะจาก `PROJECT_BRAIN.md`, `ARCHITECTURE.md`, `AGENTS.md`, `RESEARCH_LOG_FORMAT.md`, และ `IMPLEMENT_PLAN.md` หลังจาก archive แผนเดิม
2. ใช้คำตอบจากผู้ใช้เพื่อกำหนดหลักการสำคัญของ V6.34:
   - เน้นวิจัยเพื่อเพิ่มประสิทธิภาพและลดข้อผิดพลาด
   - วัดผลด้วยหลักฐานก่อน/หลังการปรับสมมติฐาน
   - sample ต้องมาจาก raw source และถ้า fetch ไม่ครบต้อง fetch ให้ครบก่อนสุ่ม
   - experiment output ไม่ใช่ production output
   - ต้องวิเคราะห์ layer ของปัญหาก่อนเลือกจุดแก้
   - ต้องจบรอบทดลองหนึ่งครั้งก่อนแก้ เพื่อให้วิเคราะห์ผลได้ตรง
   - sample pool ต้องมาจากทั้งสามเรื่อง ไม่ใช่เริ่มจากเรื่องใดเรื่องหนึ่ง
   - metric สำคัญคือความสม่ำเสมอ คุณภาพการแปล และความสามารถในการรันยาวอย่างยั่งยืน
3. สร้าง `IMPLEMENT_PLAN.md` ใหม่ และเพิ่มส่วน `V6.34 Measurement Contract`
4. เก็บแผนเดิมไว้ที่ `Backup_IMPLEMENT_PLAN/01072026_IMPLEMENT_PLAN.md`

ไม่มีการเรียก provider และไม่มีการรัน pipeline translation ในรอบนี้

## 4. ผลการศึกษาและข้อมูลดิบ

### ผลที่ดี

| รายการ | ผลลัพธ์ |
|---|---|
| แผนเดิมถูกเก็บถาวร | `Backup_IMPLEMENT_PLAN/01072026_IMPLEMENT_PLAN.md` |
| แผนใหม่ถูกสร้าง | `IMPLEMENT_PLAN.md` |
| จำนวน milestone ใหม่ | 6 milestone |
| รูปแบบการทดลอง | baseline -> analysis -> treatment -> measured rerun -> out-of-sample |
| ขอบเขต sample | DSE, HGD, IRS จาก raw source เท่านั้น |
| สถานะ MoonRead | ไม่แตะ MoonRead ในรอบนี้ |

### Metric ที่ถูก lock

| Metric | แหล่งหลักฐาน |
|---|---|
| Sentinel blocker/major/minor | scoped Sentinel reports |
| Glossary coverage failures | Libra/glossary coverage reports และ Sentinel glossary findings |
| Pronoun/name/title drift | deterministic guardrails, Sentinel, sampled manual review |
| English/CJK/Thai numeral leakage | output guardrails และ Sentinel |
| Paragraph-density/formatting failures | output guardrails และ sampled review |
| QA hard-fails | run ledger และ status reports |
| Provider failures/empty output | ledger metadata และ provider error reports |
| Manual repairs | recovery reports และ research logs |
| Wall-clock time | run reports และ timestamps |
| Provider calls per completed block | run ledger provider/stage counts |

### ผลที่ยังไม่ผ่าน

- ยังไม่ได้เริ่ม Milestone 2 source-pool audit รอบใหม่
- ยังไม่ได้สร้าง sample manifest ใหม่ตามแผนที่ refined แล้ว
- ยังไม่ได้รัน baseline round ข้ามนิยายแบบครบตามแผนใหม่

## 5. ปัญหา อุปสรรค และการแก้ไข

### ปัญหา 1: แผนเดิมยาวและปนประวัติจำนวนมาก

- สิ่งที่เกิดขึ้น: `IMPLEMENT_PLAN.md` เดิมมีประวัติ milestone เก่าจำนวนมาก ทำให้อ่านยากและไม่ตอบคำถามว่า V6.34 ต้องทำอะไรต่ออย่างชัดเจน
- วิธีแก้: archive แผนเดิม แล้วสร้างแผนใหม่ที่โฟกัสเฉพาะเส้นทาง V6.34 จาก current state ไปยังหลักฐานการปรับปรุง pipeline
- ผลลัพธ์หลังแก้: แผนใหม่สั้นลงและมี milestone ที่ตรวจรับได้

### ปัญหา 2: test suite ยังอ้างข้อความจากแผนเก่า

- สิ่งที่เกิดขึ้น: `python test_translation.py` ล้มเหลวเพราะยัง assert ข้อความเกี่ยวกับ V6.17/V6.18 ใน `IMPLEMENT_PLAN.md`
- วิธีแก้: เพิ่มส่วน `Compatibility Notes Kept For Regression Tests` แบบสั้นในท้ายแผนใหม่ เพื่อเก็บ durable lesson ที่ test คาดหวังโดยไม่ดึงประวัติยาวกลับมา
- ผลลัพธ์หลังแก้: `python test_translation.py` ผ่าน

## 6. ข้อสรุปและก้าวต่อไป

ข้อสรุป: V6.34 มีกรอบการทดลองใหม่ที่ชัดเจนขึ้นและพร้อมเข้าสู่ source-pool/sampling gate โดยยังไม่แตะ production output หรือ MoonRead

- แผนใหม่ยึด raw-source sampling ข้าม DSE, HGD, และ IRS
- การวัดผลถูก lock เป็น metric ที่มีแหล่งหลักฐานชัดเจน
- การทดลองต้องทำ baseline ให้จบรอบก่อนแก้ เพื่อให้เห็นการเปลี่ยนแปลงจริง
- Experiment output ถูกแยกจาก production output อย่างชัดเจน

ก้าวต่อไป:

1. ทำ Milestone 2: audit raw source pool ของ DSE, HGD, IRS และสร้าง sample manifest ใหม่
2. สร้างรายงาน source-pool audit ใน `07_Reports/`
3. เริ่ม baseline round เฉพาะหลัง sample manifest ถูก lock แล้ว
