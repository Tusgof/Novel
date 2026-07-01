# บันทึกการวิจัย: V6.34 M5 HGD ch132 BOM Glossary Repair

## 1. ข้อมูลพื้นฐาน

- Timestamp UTC: `2026-07-01T00:06:15Z`
- โครงการ: Novel Translation Pipeline
- หัวข้อ: V6.34 M5 HGD ch132 BOM glossary repair
- ผู้บันทึก: Codex
- สถานะ: checkpoint ผ่าน
- Artifact หลัก:
  - `07_Reports/v6_34_m5_hgd_treatment_ch132_bom_glossary_repair_20260701.md`
  - `Horror Game Developers/04_Work/_experiments/v6_34_m5_hgd_treatment_v1/07_Reports/sentinel_quality_v6-34-m5-hgd-treatment-v1_ch132_sentinel_20260701_000506.md`
  - `Horror Game Developers/04_Work/_experiments/v6_34_m5_hgd_treatment_v1/05_Output/ch132/ch132.md`

## 2. วัตถุประสงค์

รอบนี้ต้องการแก้ treatment failure ของ HGD `ch132` โดยไม่ patch final output เอง และต้องแยกว่า defect เป็นปัญหา multi-novel หรือ novel-specific

ความสำเร็จคือ `ch132` ต้องกลับมาผ่าน Sentinel `0/0/0/0` ด้วย pipeline rerun และต้องมี regression test กันไม่ให้ glossary note แบบเดียวกันถูกข้ามอีก

## 3. วิธีการและขั้นตอน

1. ตรวจ source `Horror Game Developers/03_Raw/ch132/source.json` ยืนยันว่าต้นฉบับมี `Hoarding Department`, `Collection Department`, `Sarah Sorloth`, และ `Sarah`
2. ตรวจ output และ Sentinel report พบ output ใช้ loose variants:
   - `แผนกสะสม`
   - `แผนกจัดเก็บ`
   - `ซาร่าห์`
   - `ซาร่าห์ ซอร์ลอธ`
3. ตรวจ glossary index ของ experiment ด้วยสคริปต์ Python แบบ read-only พบว่า index ไม่โหลด notes กลุ่มนี้
4. ตรวจ raw prefix ของ glossary notes พบ UTF-8 BOM (`\ufeff---`) ทำให้ parser ไม่ผ่าน `raw.startswith("---")`
5. แก้ parser ให้ strip BOM ก่อนตรวจ frontmatter
6. เพิ่ม `rejected_variants` ใน HGD glossary notes ที่เกี่ยวข้อง และแก้ `Kaelen.md` body ให้ตรงกับ approved `thai_term`
7. รัน verification:

```powershell
cd "D:\Fogust\Workspace\Novel\Deep Sea Embers"
$env:PYTHONIOENCODING='utf-8'
python -m compileall novel_pipeline
python test_translation.py
```

8. sync glossary notes เข้า experiment vault แล้ว rerun:

```powershell
cd "D:\Fogust\Workspace\Novel\Horror Game Developers\04_Work\_experiments\v6_34_m5_hgd_treatment_v1"
$env:PYTHONIOENCODING='utf-8'
novel-pipeline --config ".system/config.yaml" rerun-block --run-id v6-34-m5-hgd-treatment-v1 --block-id ch132-block-001 --from-stage refining
novel-pipeline --config ".system/config.yaml" status --run-id v6-34-m5-hgd-treatment-v1
```

## 4. ผลการศึกษาและข้อมูลดิบ

| Metric | Before | After |
|---|---|---|
| `ch132` Sentinel blocker/major/minor/info | `3/2/0/0` | `0/0/0/0` |
| Current failed blocks | `ch132-block-001` blocked by Sentinel | none |
| Completed treatment chapters | `ch024`, `ch037`, `ch066`, `ch103` | `ch024`, `ch037`, `ch066`, `ch103`, `ch132` |
| Pending treatment chapters | `ch142`, `ch170`, `ch196`, `ch225`, `ch250` | unchanged |

Verified output now contains:

- `แผนกกักเก็บ`
- `แผนกรวบรวม`
- `ซาราห์ ซอร์ลอธ`
- `ซาราห์`

## 5. ปัญหา อุปสรรค และการแก้ไข

1. ปัญหา: glossary notes ที่มี UTF-8 BOM ถูก parser ข้ามทั้งไฟล์
   - การแก้ไข: `parse_glossary_note()` strip BOM ด้วย `.lstrip("\ufeff")`
   - ผลลัพธ์: glossary index โหลด `Sarah`, `Sarah Sorloth`, `Hoarding Department`, และ `Collection Department` ได้

2. ปัญหา: HGD loose variants ไม่ถูกบันทึกเป็น rejected variants
   - การแก้ไข: เพิ่ม rejected variants ใน glossary notes
   - ผลลัพธ์: prompt/subset เห็น policy ชัดขึ้น และ rerun ผลิต output ที่ผ่าน Sentinel

3. ปัญหา: `Kaelen.md` body ขัดกับ frontmatter
   - การแก้ไข: body เปลี่ยนเป็น `Use เคเลน consistently`
   - ผลลัพธ์: regression test ยืนยัน note ไม่ขัดกับตัวเอง

ข้อจำกัดสำคัญ: รอบนี้เป็น HGD treatment slice เท่านั้น ยังไม่ได้สรุปว่า treatment ทั้ง M5 ผ่านครบทุก in-sample chapter

## 6. ข้อสรุปและก้าวต่อไป

ข้อสรุป: `ch132` failure เป็น defect ผสมระหว่าง Layer 0 parser robustness และ Layer 2 HGD glossary policy ซึ่งแก้แล้วและมีหลักฐาน Sentinel ดีขึ้นจาก `3/2/0/0` เป็น `0/0/0/0`

- BOM-tolerant parser เป็น improvement ระดับ multi-novel เพราะช่วย glossary note ทุกเรื่อง
- rejected variants เป็น policy เฉพาะ HGD เพราะคำเหล่านี้มาจาก convention ของเรื่องนี้
- treatment ยังไม่จบทั้ง M5 แต่ผ่าน checkpoint เพิ่มอีกหนึ่งจุด

ก้าวต่อไป:
1. Continue M5 treatment rerun จาก `ch142`
2. หยุดทันทีถ้าเจอ Sentinel blocker/major หรือ manual QA prompt
3. หลังครบ HGD in-sample ให้สรุป metric movement เทียบ baseline ก่อนแตะ DSE/IRS treatment
