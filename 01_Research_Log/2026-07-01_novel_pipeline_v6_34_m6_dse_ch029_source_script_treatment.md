# บันทึกการวิจัย: V6.34 M6 DSE ch029 source-script annotation treatment

## 1. ข้อมูลพื้นฐาน

- Timestamp UTC: `2026-07-01T10:47:00Z`
- โครงการ: Novel Translation Pipeline
- หัวข้อ: DSE OOS `ch029-block-005` source-script annotation leakage
- ผู้บันทึก: Codex
- สถานะ: เสร็จสิ้น
- Artifact หลัก:
  - `07_Reports/v6_34_m6_dse_oos_ch029_source_script_treatment_20260701.md`
  - `Deep Sea Embers/novel_pipeline/pipeline.py`
  - `Deep Sea Embers/test_translation.py`
  - `Deep Sea Embers/04_Work/_experiments/v6_34_m6_dse_oos_v2/04_Work/ch029/ch029-block-005.refined.json`
  - `Deep Sea Embers/04_Work/_experiments/v6_34_m6_dse_oos_v2/05_Output/ch029/ch029.md`

## 2. วัตถุประสงค์

รอบนี้ต้องแก้ QA hard-fail ของ DSE OOS v2 ที่ `ch029-block-005` โดยไม่ force-accept และไม่แก้ final output แบบ manual patch

ความสำเร็จคือระบบต้องป้องกัน Chinese source-script annotation ที่หลุดใน output ได้ด้วยกลไก deterministic, test ผ่าน, rerun block ผ่าน QA, และ output หลังแก้ไม่มี Han Chinese

## 3. วิธีการและขั้นตอน

1. ตรวจ `status` และ `inspect-block` หลัง resume v2 หยุดที่ `ch029-block-005`
2. อ่าน `literal.json`, `refined.json`, `qa.json`, และ source tail ของ `ch029`
3. ระบุ pattern ที่ทำให้ QA fail:

```text
"ก้าวสู่ความไม่เป็นวิทยาศาสตร์" [走进不科学]
```

4. เพิ่ม helper `_apply_source_script_annotation_repairs()` ใน pipeline เพื่อ remove bracket/parenthesis/book-title CJK annotation แคบ ๆ หลังมี Thai wording แล้ว
5. เพิ่ม regression test ใน `test_translation.py`
6. รัน verification:

```powershell
python -m compileall novel_pipeline
$env:PYTHONIOENCODING='utf-8'
python test_translation.py
```

7. Rerun block:

```powershell
novel-pipeline --config ".system/config.yaml" rerun-block --run-id v6-34-m6-dse-oos-v2 --block-id ch029-block-005 --from-stage refine
```

8. ตรวจ refined/formatted/final output ว่าไม่มี Han Chinese

## 4. ผลการศึกษาและข้อมูลดิบ

| Metric | Before | After |
|---|---:|---:|
| Current failed blocks | 1 | 0 |
| `ch029-block-005` QA | hard_fail | passed retry 2 |
| `ch029-block-005.formatted.json` | missing | exists |
| `05_Output/ch029/ch029.md` | missing | exists |
| Han Chinese in refined output | yes | no |
| Han Chinese in formatted output | not available | no |
| Han Chinese in final chapter output | not available | no |

Validation results:

- `python -m compileall novel_pipeline`: passed
- `python test_translation.py`: passed

## 5. ปัญหา อุปสรรค และการแก้ไข

1. **อาการ:** QA hard-fail เพราะ refined output ยังมี Chinese/Japanese/Korean source characters
   - **การแก้ไข:** เพิ่ม deterministic cleanup สำหรับ bracketed source-script annotation
   - **ผลลัพธ์:** rerun block ผ่าน QA และ output ไม่มี Han Chinese

2. **อาการ:** local literal-safe recovery เก็บ Chinese title annotation มาจาก literal pair เพราะเห็นว่าเป็นส่วนหนึ่งของ source sentence
   - **การแก้ไข:** ใส่ cleanup หลัง refine/recovery ก่อน QA แทนการ manual patch
   - **ผลลัพธ์:** กลไกนี้ใช้ซ้ำกับ block อื่นได้ถ้าเกิด pattern เดียวกัน

ข้อจำกัดสำคัญ:

- นี่ไม่ใช่การอนุมัติให้ strip CJK จาก source ก่อนแปลทั้งหมด เฉพาะ leaked annotation ใน output หลังมี Thai wording แล้วเท่านั้น
- DSE OOS v2 ยังไม่จบทั้ง 10 chapters ต้อง resume ต่อจาก `ch047`

## 6. ข้อสรุปและก้าวต่อไป

ข้อสรุป: ปัญหา `ch029-block-005` เป็น output-side source-script annotation leakage ที่แก้ได้ด้วย deterministic cleanup แคบ ๆ และ verified แล้ว

- ไม่ต้อง force-accept QA
- ไม่ต้องแก้ production output
- กลไกนี้ช่วยลด CJK leakage ซ้ำใน DSE/นิยายอื่นโดยไม่ลดคุณภาพการแปล

ก้าวต่อไป:

1. Commit/push treatment code, report, and research log
2. Resume DSE OOS v2 จาก next pending `ch047`
3. ถ้าเจอ pattern ใหม่ ให้หยุด วิเคราะห์ layer และเพิ่ม guard เท่าที่จำเป็นเท่านั้น
