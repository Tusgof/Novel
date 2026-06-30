# บันทึกการวิจัย: V6.34 M4 เลือก Treatment สำหรับ Title/Glossary Drift

## 1. ข้อมูลพื้นฐาน

- Timestamp UTC: `2026-07-01T00:00:00Z`
- โครงการ: Novel Translation Pipeline
- หัวข้อ: V6.34 M4 treatment selection
- ผู้บันทึก: Codex
- สถานะ: เสร็จสิ้น
- Artifact หลัก:
  - `07_Reports/v6_34_m4_treatment_selection_title_glossary_20260701.md`
  - `Deep Sea Embers/novel_pipeline/pipeline.py`
  - `Deep Sea Embers/test_translation.py`

## 2. วัตถุประสงค์

เป้าหมายของรอบนี้คือเลือก treatment ที่เล็กที่สุดจาก defect analysis ของ HGD `ch037` เพื่อป้องกัน title/H1 ใช้คำไทยไม่ตรงกับ approved glossary

รอบนี้ไม่ใช่ production repair และไม่ publish MoonRead

## 3. วิธีการและขั้นตอน

1. ตรวจ baseline evidence ของ HGD `ch037`
2. ตรวจ source title, glossary note, title sidecar, final H1, และ QA artifact
3. เลือก treatment ตาม layer:
   - Layer 0: runtime title/H1 glossary validation
   - Layer 2: HGD title map correction
4. เพิ่ม regression test ที่จำลอง sidecar ผิด `เวลอรา` เมื่อ glossary approved คือ `เวโลรา`
5. รัน compile และ test suite

## 4. ผลการศึกษาและข้อมูลดิบ

| Item | Result |
|---|---|
| Treatment selected | deterministic title/H1 glossary validation |
| HGD canonical correction | `Velora Art Museum -> พิพิธภัณฑ์ศิลปะเวโลรา` |
| Regression test | sidecar ที่ผิด glossary ถูก block ก่อน final assembly |
| Compile | passed |
| `python test_translation.py` | passed |

ผลที่คาดหวัง: ลด Sentinel major จาก title glossary coverage miss โดยไม่ลดคุณภาพเนื้อแปล เพราะ treatment ไม่แตะ body prose

## 5. ปัญหา อุปสรรค และการแก้ไข

ปัญหาหลักคือ final assembly เคยเชื่อ `title.json` ทันที ถ้าไฟล์นั้นมี Thai title อยู่แล้ว จึงทำให้ title sidecar ที่ผิด glossary หลุดไปถึง final output ได้

การแก้คือเพิ่ม guard ก่อนคืนค่า title ทุกครั้งที่มี source title และ glossary directory: ถ้า source title มี approved term หรือ alias แต่ resolved title ไม่มี `thai_term` ให้หยุดทันที

## 6. ข้อสรุปและก้าวต่อไป

M4 treatment selection เสร็จแล้ว และ implementation slice แรกผ่าน test

ก้าวต่อไปคือ M5: สร้างหรือ sync treatment experiment vault แล้ว rerun treatment เทียบ baseline ด้วย metric เดิม ห้าม patch baseline history และห้าม publish experiment output ไป MoonRead
