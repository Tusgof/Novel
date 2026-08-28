# บันทึกการวิจัย: Immortality System Libra - Pilot Gate

## 1. ข้อมูลพื้นฐาน

- Timestamp UTC: `2026-08-28T09:23:33Z`
- โครงการ: Novel Translation Pipeline
- หัวข้อ: Immortality System mandatory Libra - Pilot Gate completion
- ผู้บันทึก: Codex
- สถานะ: เสร็จสิ้น (experiment-only)
- เครื่องมือ: bounded pipeline, deterministic output guardrails, blocking Sentinel
- Artifact หลัก:
  - `07_Reports/immortality_system_libra_pilot_completion_20260828.md`
  - `07_Reports/libra_pilot_gate_sample_20260828.md`
  - `07_Reports/libra_pilot_gate_sample_20260828.json`
  - `Immortality System/04_Work/_experiments/libra_pilot_immortality_system_v1/06_Logs/run_ledger.jsonl`

## 2. วัตถุประสงค์

รอบนี้มีเป้าหมายเพื่อตรวจว่า Immortality System ผ่าน setup gate ที่จำเป็นก่อน
เริ่ม production หรือไม่ โดยใช้บทที่สุ่มจาก raw source จริง แยก in-sample สำหรับ
การปรับ pipeline และ out-of-sample สำหรับตรวจการนำไปใช้กับบทที่ไม่ถูกใช้ปรับแต่ง

เกณฑ์ผ่านคือทุกบทและทุก block ในทั้งสองชุดต้องจบโดยไม่มี failure ค้าง, source parity
ต้องเป็นศูนย์, output guardrails และ blocking Sentinel ต้องผ่าน และต้องตรวจว่าปัญหา
จาก provider/fallback ไม่ทำให้ output ที่ไม่ปลอดภัยถูกยอมรับ

## 3. วิธีการและขั้นตอน

1. ตรวจ raw source ของ Novel543 จนถึง `ch2570` และยืนยันว่ามีบทที่ใช้งานได้
   `2570/2570` บท
2. ใช้ seed `20260828` สุ่มจาก experiment copy ของ `03_Raw/` แบบ stratified
   แล้วล็อก 10 in-sample และ 10 out-of-sample บท
3. ตรวจ source parity ของบทที่สุ่มกับ raw source ต้นฉบับ และได้ `0` mismatches
4. รัน scan/glossary approval gate แยกจาก production และไม่ promote candidate
   generic เข้า production glossary โดยอัตโนมัติ
5. รัน bounded translation, refinement, QA, AI formatting, deterministic checks
   และ blocking Sentinel ใน experiment vault เดิมจนทั้งสองชุดจบ
6. ตรวจ checkpoint, provider usage, cleanliness, glossary audit และ Sentinel closure
   report; ทำ manual spot-check 5 บทจาก OOS (`ch1410`, `ch2313`, `ch1653`,
   `ch1984`, `ch282`)

คำสั่งตรวจหลักที่ใช้:

```powershell
python "Immortality System\04_Work\_experiments\libra_pilot_immortality_system_v1\scripts\verify_experiment_source_parity.py" --novel-root "Immortality System" --experiment-root "Immortality System\04_Work\_experiments\libra_pilot_immortality_system_v1" --chapters ch1307,ch1765,ch2439,ch2307,ch741,ch1424,ch1631,ch376,ch338,ch984,ch1410,ch1020,ch2313,ch2358,ch1149,ch1653,ch1984,ch213,ch544,ch282
python -m compileall "Deep Sea Embers\novel_pipeline"
python "Deep Sea Embers\test_translation.py"
```

การรันทั้งหมดอยู่ใน experiment vault และไม่เรียก publish ไป MoonRead

## 4. ผลการศึกษาและข้อมูลดิบ

### ผลเปรียบเทียบระหว่างชุดทดลอง

| Metric | In-sample | Out-of-sample |
|:--|:--:|:--:|
| Chapters | 10/10 | 10/10 |
| Blocks | 42/42 | 40/40 |
| Current failed blocks | 0 | 0 |
| Historical failed records | 3, recovered | 0 |
| Source parity mismatches | 0 | 0 |
| Output cleanliness | 10/10 clean | 10/10 clean |
| Sentinel blocker/major/minor/info | 0/0/0/0 | 0/0/0/0 |
| Final Sentinel safe to publish | yes | yes |

### Reliability and glossary observations

- In-sample มี OpenRouter empty-assistant refinement failure 3 รายการใน ledger
  แต่ recovery สำเร็จทั้งหมดและไม่มี force-accept
- OOS ไม่มี historical failed ledger record; fallback provider ถูกบันทึกใน metadata
- title sidecar ของ sample ทั้ง 20 บทผ่านการตรวจและ final assembly จบครบ
- glossary audit พบ exact-match variation ของคำทั่วไป เช่น `紀元`, `五姓`, `有人`,
  `九域`; ไม่พบ suspicious wrong variant หรือ Sentinel blocker/major จากประเด็นนี้
- manual spot-check OOS 5 บทไม่พบ title/body leakage, Thai numeral drift,
  truncation ที่เห็นได้ชัด หรือ paragraph-density failure

หลักฐานดิบและรายงานเต็มอยู่ที่:

- `07_Reports/immortality_system_libra_pilot_completion_20260828.md`
- `Immortality System/04_Work/_experiments/libra_pilot_immortality_system_v1/07_Reports/immortality_libra_pilot_insample_checkpoint_20260828.md`
- `Immortality System/04_Work/_experiments/libra_pilot_immortality_system_v1/07_Reports/immortality_libra_pilot_oos_checkpoint_20260828.md`
- `Immortality System/04_Work/_experiments/libra_pilot_immortality_system_v1/07_Reports/immortality_libra_pilot_insample_cleanliness_20260828.md`
- `Immortality System/04_Work/_experiments/libra_pilot_immortality_system_v1/07_Reports/immortality_libra_pilot_oos_cleanliness_20260828.md`
- `Immortality System/04_Work/_experiments/libra_pilot_immortality_system_v1/07_Reports/immortality_libra_pilot_insample_glossary_audit_20260828.md`
- `Immortality System/04_Work/_experiments/libra_pilot_immortality_system_v1/07_Reports/immortality_libra_pilot_oos_glossary_audit_20260828.md`

### สิ่งที่ยังไม่ได้วัด

รอบนี้ไม่ได้ทำ causal baseline-versus-treatment comparison ภายใน IRS setup pilot
และไม่ได้ทดสอบ broad unattended parallel translation/refinement/QA ดังนั้นผลนี้
ยืนยันความพร้อมของ gate และการ generalize ใน sample นี้ แต่ยังไม่ใช่หลักฐานว่า
pipeline ดีกว่า provider/routing เดิมในทุกมิติหรือพร้อมรันยาวแบบไร้การดูแล

## 5. ปัญหา อุปสรรค และการแก้ไข

1. OpenRouter ส่ง empty assistant ระหว่าง title/refinement บางครั้ง
   - อาการ: bounded attempt หยุดแบบ fail-closed และไม่เขียน artifact สำเร็จปลอม
   - การแก้ไข: ให้ title helper เดิน fallback ที่ตั้งค่าไว้และคืน provider/model ที่ใช้จริง
     พร้อม regression test
   - ผลลัพธ์: title sidecar ทั้ง 20 บท valid และ final assembly ผ่าน
2. Glossary provider บางรอบไม่มี safe Thai option และ fallback Claude ใช้งานไม่ได้
   เพราะ OAuth หมดอายุ
   - อาการ: glossary approval หยุดที่ term เดียวโดยไม่สร้าง `glossary_approved`
   - การแก้ไข: resume จาก ledger เดิมหลัง route ที่ใช้งานได้กลับมา โดยยัง fail-closed
     เมื่อไม่มี option ที่ปลอดภัย
   - ผลลัพธ์: in-sample และ OOS จบครบ ไม่มี current failure
3. title sidecar ของ `ch1424` รอบแรกใช้คำแปลเก่าที่ไม่ตรง approved glossary
   - อาการ: validation ปฏิเสธ sidecar
   - การแก้ไข: rerun title pipeline หลัง glossary approval แล้วตรวจ assembly ซ้ำ
   - ผลลัพธ์: sidecar ผ่านและไม่ปล่อยชื่อเก่าเข้า output
4. การเรียก Sentinel ใน experiment vault ต้องชี้ registry และ report root ให้ตรง vault
   - อาการ: helper เดิมตรวจเฉพาะ root ตรง ทำให้ nested experiment layout เปราะบาง
   - การแก้ไข: เพิ่ม experiment-aware parent resolution ใน
     `Deep Sea Embers/novel_pipeline/pipeline.py` และ regression tests ใน
     `Deep Sea Embers/test_translation.py`
   - ผลลัพธ์: Sentinel final ของทั้งสองชุดเป็น `0/0/0/0` และ production workspace
     ไม่ถูก override

ข้อจำกัดสำคัญ: experiment output ไม่ใช่ production output, ไม่ได้ publish MoonRead,
และไม่อนุมัติการเปลี่ยน provider routing หรือการเปิด concurrency

## 6. ข้อสรุปและก้าวต่อไป

ข้อสรุป: Immortality System ผ่าน Libra - Pilot Gate ด้านคุณภาพและการ generalize
สำหรับ sample 20 บท แต่ควรเริ่ม production ด้วย bounded sequential mode เท่านั้น

- ทุกบทที่ล็อกไว้จบครบและไม่มี failure ค้าง
- blocking Sentinel และ deterministic output gates ผ่านทั้ง in-sample/OOS
- ปัญหา provider ที่พบถูกบันทึกและกู้คืนโดยไม่ force-accept
- ผลยังไม่พิสูจน์ความเร็วหรือความเสถียรของ parallel unattended run

ก้าวต่อไป:
1. รอช่วงบท production ที่ผู้ใช้อนุมัติอย่างชัดเจน แล้วเริ่ม scan-only gate ใหม่
2. ใช้ bounded sequential batch พร้อม glossary gate ทุก 5 บท
3. รัน output guardrails, blocking Sentinel และ major-run spot-check ก่อน publish
4. แยกการทดลอง parallel ออกเป็น benchmark ใหม่ หากต้องการเพิ่ม throughput
