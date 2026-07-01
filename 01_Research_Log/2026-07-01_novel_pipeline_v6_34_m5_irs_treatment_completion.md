# บันทึกการวิจัย: V6.34 M5 IRS Treatment Completion

## 1. ข้อมูลพื้นฐาน

- Timestamp UTC: `2026-07-01T05:40:41Z`
- โครงการ: Novel Translation Pipeline
- หัวข้อ: V6.34 Milestone 5 IRS treatment completion
- ผู้บันทึก: Codex
- สถานะ: เสร็จสิ้น
- Artifact หลัก:
  - `07_Reports/v6_34_m5_irs_treatment_completion_20260701.md`
  - `Infinite Regressor Stories/04_Work/_experiments/v6_34_m5_irs_treatment_v1/07_Reports/sentinel_quality_v6-34-m5-irs-treatment-v1_all_in_sample_final_20260701_053858.md`
  - `Infinite Regressor Stories/04_Work/_experiments/v6_34_m5_irs_treatment_v1/06_Logs/run_ledger.jsonl`

## 2. วัตถุประสงค์

รอบนี้ต้องตอบว่า IRS treatment ใน Milestone 5 สามารถจบ in-sample 10 ตอนอย่างถูกต้องหลังแก้ blocker `Footnotes:` ได้หรือไม่ และผลลัพธ์มีหลักฐานพอสำหรับนำไปเปรียบเทียบกับ HGD/DSE treatment ก่อนเปิด Milestone 6 out-of-sample หรือยัง

ความสำเร็จของรอบนี้คือ sampled chapters ทั้ง 10 ต้องจบใน isolated experiment vault, ไม่มี current failed block, source parity ต้องเป็นศูนย์ mismatch, Sentinel ต้องไม่มี blocker/major, และ output ต้องไม่มี CJK/provider/meta/เลขไทย/quote-only leakage

## 3. วิธีการและขั้นตอน

1. ตรวจและเติม experiment-local title sidecar สำหรับ IRS sampled chapters หลัง `ch020` เพื่อไม่ให้ final assembly หยุดเพราะ title metadata ขาด
2. Resume ทีละ chapter boundary เพื่อหยุดได้ทันเมื่อพบ QA hard-fail หรือ provider failure
3. เมื่อพบ QA hard-fail จาก CJK parenthetical leakage ที่ `ch080-block-003` และ `ch261-block-001` ให้ rerun จาก `refine` ซึ่งเป็น earliest safe stage สำหรับ defect นี้
4. หลังครบทุก chapter รัน status, source parity, deterministic output checks และ Sentinel รวมทั้ง sample

คำสั่งหลัก:

```powershell
novel-pipeline --config ".system/config.yaml" resume --run-id v6-34-m5-irs-treatment-v1 --until-chapter ch361 --manual-action-mode stop
novel-pipeline --config ".system/config.yaml" status --run-id v6-34-m5-irs-treatment-v1
python scripts/verify_experiment_source_parity.py --novel-root "D:\Fogust\Workspace\Novel\Infinite Regressor Stories" --experiment-root "D:\Fogust\Workspace\Novel\Infinite Regressor Stories\04_Work\_experiments\v6_34_m5_irs_treatment_v1" --chapters "ch020,ch067,ch080,ch119,ch160,ch207,ch261,ch276,ch322,ch361"
python scripts\sentinel_quality_report.py --scope v6-34-m5-irs-treatment-v1_all_in_sample_final --novel infinite-regressor-stories --chapters ch020,ch067,ch080,ch119,ch160,ch207,ch261,ch276,ch322,ch361 --fail-on major --skip-advisory-english
```

## 4. ผลการศึกษาและข้อมูลดิบ

### ผลที่ดี

| Metric | Result |
|---|---:|
| sampled chapters | 10 |
| completed blocks | 32/32 |
| current failed blocks | 0 |
| manual actions needed | 0 |
| source parity mismatches | 0 |
| final Sentinel blocker/major/minor/info | 0/0/1/0 |
| CJK leakage in final output | 0 |
| Thai numeral leakage in final output | 0 |
| provider/meta/glossary-note leakage | 0 |
| quote-only lines | 0 |

### Provider และ recovery data

| Metric | Result |
|---|---:|
| OpenRouter translating completed | 32 |
| OpenRouter refining completed | 48 |
| OpenRouter refining failed | 2 |
| OpenRouter QA completed | 32 |
| OpenRouter formatting completed | 26 |
| local formatting completed | 6 |
| local_recovery refining completed | 4 |
| QA hard-fail records | 2 |

### ผลที่ยังไม่ผ่านเต็มที่

- Sentinel รวมทั้ง sample ยังมี minor 1 รายการ: `Complete Memory -> ความทรงจำสมบูรณ์` missing ใน `ch207`
- `ch080-block-003` และ `ch261-block-001` เกิด QA hard-fail เพราะ refined output เก็บ Hanja/Han parenthetical source annotations
- ยังมี provider failure historical 2 รายการ: mojibake Thai output และ empty OpenRouter assistant message

## 5. ปัญหา อุปสรรค และการแก้ไข

1. Missing title sidecar
   - อาการ: `ch067` เคย assemble ไม่ได้เพราะไม่มี `title.json`
   - การแก้: สร้าง experiment-local title sidecar สำหรับ sampled chapters ที่เหลือ
   - ผลลัพธ์: final assembly ผ่านจนจบทุก chapter

2. CJK parenthetical leakage
   - อาการ: QA hard-fail ที่ `ch080-block-003` และ `ch261-block-001`
   - การแก้: rerun จาก `refine`
   - ผลลัพธ์: ทั้งสอง block ผ่าน QA retry 0 หลัง rerun และ final output ไม่มี CJK leakage

3. Provider malformed output
   - อาการ: OpenRouter refining failed 2 ครั้งจาก mojibake output และ empty assistant message
   - การแก้: ใช้ retry/rerun ตาม pipeline recovery
   - ผลลัพธ์: ไม่มี current failed block เหลืออยู่

ข้อจำกัดสำคัญ: รอบนี้เป็น treatment in-sample เท่านั้น ยังไม่ใช่หลักฐานว่า generalize ไป out-of-sample หรือ production long-run ได้ ต้องทำ Milestone 5 comparison รวม HGD/DSE/IRS ก่อน แล้วจึงเปิด Milestone 6

## 6. ข้อสรุปและก้าวต่อไป

ข้อสรุป: IRS treatment in-sample จบครบและปลอด blocker/major แต่ยังมีหลักฐานว่า long-run smoothness และ glossary coverage ยังต้องปรับก่อนสเกล

- Output surface ดีขึ้นหลังแก้ `Footnotes:` blocker: ไม่มี CJK/meta/เลขไทย/quote-only leakage
- Runtime Sentinel ทำงานแล้วและจับ minor glossary coverage ได้
- QA hard-fail จาก Hanja/Han parenthetical leakage เป็น pattern ที่ควรถูกจัดชั้นเป็น Layer 1/Layer 0 candidate หลังเทียบสามเรื่อง
- Provider empty/mojibake output ยังเป็น risk ของ long-run execution

ก้าวต่อไป:

1. สร้าง Milestone 5 comparison รวม HGD, DSE, และ IRS treatment metrics
2. ตัดสินว่า M5 treatment พอเปิด Milestone 6 OOS หรือควรเพิ่ม treatment rule ก่อน
3. ถ้าเปิด M6 ให้ใช้ out-of-sample set ที่ล็อกไว้และห้าม tune ระหว่างรอบ
