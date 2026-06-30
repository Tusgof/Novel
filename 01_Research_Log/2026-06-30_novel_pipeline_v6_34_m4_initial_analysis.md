# บันทึกการวิจัย: V6.34 M4 วิเคราะห์ HGD ch037 หลัง Baseline Stop

## 1. ข้อมูลพื้นฐาน

- Timestamp UTC: `2026-06-30T22:52:27Z`
- โครงการ: Novel Translation Pipeline
- หัวข้อ: V6.34 M4 initial defect analysis
- ผู้บันทึก: Codex
- สถานะ: เสร็จสิ้น
- Artifact หลัก:
  - `07_Reports/v6_34_m4_initial_defect_analysis_hgd_ch037_20260701.md`
  - `07_Reports/sentinel_quality_manual_experiment_ch037_probe_20260630_224633.md`

## 2. วัตถุประสงค์

รอบนี้มีเป้าหมายเพื่อเริ่ม Milestone 4 โดยวิเคราะห์ defect ที่ทำให้ M3 baseline หยุดที่ HGD `ch037` และแยกให้ชัดว่าปัญหาอยู่ใน layer ไหน ก่อนจะเลือก treatment

สิ่งที่ต้องตอบคือ Sentinel major เกิดจาก body translation, glossary prompt, title sidecar, หรือ Sentinel instrumentation กันแน่

## 3. วิธีการและขั้นตอน

1. อ่าน Sentinel report ของ `ch037`
2. ตรวจ source title ใน `03_Raw/ch037/source.json`
3. ตรวจ approved glossary note `01_Glossary/Velora Art Museum.md`
4. ตรวจ title sidecar ทั้ง production copy และ experiment copy
5. ตรวจ final output H1 ใน experiment `05_Output/ch037/ch037.md`
6. ตรวจ QA artifact เพื่อดูว่า QA ผ่านเพราะตรวจ body ไม่ครอบคลุม final title หรือไม่
7. เขียนรายงาน analysis ที่ `07_Reports/v6_34_m4_initial_defect_analysis_hgd_ch037_20260701.md`

## 4. ผลการศึกษาและข้อมูลดิบ

| Item | Result |
|---|---|
| Source title | `Chapter 37 - Velora Art Museum [2]` |
| Approved glossary | `Velora Art Museum -> พิพิธภัณฑ์ศิลปะเวโลรา` |
| Title sidecar | `ตอนที่ 37 - พิพิธภัณฑ์ศิลปะเวลอรา` |
| Final H1 | `# ตอนที่ 37 - พิพิธภัณฑ์ศิลปะเวลอรา` |
| QA result | PASS, but did not flag title glossary miss |
| Sentinel result after experiment-local probe | blocker/major/minor/info `0/2/0/0` |

Layer classification:

| Defect | Layer |
|---|---|
| Title sidecar conflicts with approved glossary | Layer 2: HGD novel artifact/profile |
| Sentinel originally scanned production output from experiment run | Layer 0: shared guardrail infrastructure |
| QA did not inspect final title/H1 | Layer 0 or Layer 3, depending on chosen treatment |

## 5. ปัญหา อุปสรรค และการแก้ไข

ไม่พบปัญหาใหม่ในรอบ analysis นี้

ข้อจำกัดสำคัญ:

- ยังไม่ได้แก้ title sidecar เพราะนี่เป็น analysis round ไม่ใช่ treatment round
- ยังไม่ได้ rerun baseline หลัง treatment เพราะ treatment ยังไม่ได้รับการเลือก

## 6. ข้อสรุปและก้าวต่อไป

ข้อสรุป: `ch037` baseline stop เกิดจาก title sidecar ใช้คำไทยไม่ตรง glossary ที่ approved แล้ว ไม่ใช่ body translation miss

- ปัญหาหลักเป็น Layer 2 HGD title/glossary consistency
- ปัญหา Sentinel scoping เป็น Layer 0 infrastructure และแก้แล้วเพื่อให้ analysis ถูก path
- Treatment ที่เหมาะคือ title/glossary guard + HGD title sidecar repair ในรอบ treatment ไม่ใช่ patch baseline

ก้าวต่อไป:

1. เลือก treatment hypothesis จากรายงาน M4
2. เพิ่ม deterministic title/glossary validation ที่ไม่ลดคุณภาพการแปล
3. ทำ treatment rerun หลัง fix ถูกกำหนดชัดเจน
