# บันทึกการวิจัย: V6.34 M6 HGD OOS จบครบ 10 ตอน

## 1. ข้อมูลพื้นฐาน

- Timestamp UTC: `2026-07-01T08:29:39Z`
- โครงการ: Novel Translation Pipeline
- หัวข้อ: V6.34 M6 HGD OOS completion
- ผู้บันทึก: Codex
- สถานะ: เสร็จสิ้น
- Artifact หลัก:
  - `07_Reports/v6_34_m6_hgd_oos_completion_20260701.md`
  - `Horror Game Developers/04_Work/_experiments/v6_34_m6_hgd_oos_v1/06_Logs/run_ledger.jsonl`
  - `Horror Game Developers/04_Work/_experiments/v6_34_m6_hgd_oos_v1/07_Reports/sentinel_quality_v6-34-m6-hgd-oos-v1_*_sentinel_*.json`

## 2. วัตถุประสงค์

รอบนี้ต้องสรุปว่า HGD out-of-sample slice ของ V6.34 สามารถจบครบ 10 ตอนหลัง treatment หลายรอบได้หรือไม่ และผลลัพธ์บอกอะไรเกี่ยวกับความพร้อมของ pipeline สำหรับการรันยาวแบบยั่งยืน

ความสำเร็จคือทุก chapter ใน HGD OOS มี output ใน experiment vault, ไม่มี current failed blocks, Sentinel latest เป็น `0/0/0/0`, และไม่มี provider/meta leakage หรือ Han Chinese body text ใน output ทดลอง

## 3. วิธีการและขั้นตอน

1. ตรวจ status ของ run `v6-34-m6-hgd-oos-v1`

```powershell
cd "D:\Fogust\Workspace\Novel\Horror Game Developers\04_Work\_experiments\v6_34_m6_hgd_oos_v1"
$env:PYTHONIOENCODING='utf-8'
novel-pipeline --config ".system/config.yaml" status --run-id v6-34-m6-hgd-oos-v1
```

2. อ่าน latest Sentinel JSON ของทุก chapter ใน sample
3. อ่าน QA artifact ของทุก chapter
4. ตรวจ final experiment output แบบ deterministic พื้นฐาน:
   - Han Chinese body text
   - provider/meta leakage
   - quote-only line
5. นับ provider/stage records จาก experiment ledger

## 4. ผลการศึกษาและข้อมูลดิบ

### สถานะ run

| Metric | Value |
|---|---:|
| Records | `145` |
| Completed blocks | `10/10` |
| Current failed blocks | `0` |
| Historical failed records | `4` |
| Manual actions needed | none |

### Completed chapters

| Chapter | Status | Latest Sentinel |
|---|---|---|
| `ch015` | complete | `0/0/0/0` |
| `ch046` | complete | `0/0/0/0` |
| `ch060` | complete | `0/0/0/0` |
| `ch101` | complete | `0/0/0/0` |
| `ch131` | complete after treatment | `0/0/0/0` |
| `ch153` | complete | `0/0/0/0` |
| `ch184` | complete after treatment | `0/0/0/0` |
| `ch192` | complete after treatment | `0/0/0/0` |
| `ch226` | complete | `0/0/0/0` |
| `ch262` | complete | `0/0/0/0` |

### Provider/stage evidence

| Provider | Stage | Status | Count |
|---|---|---|---:|
| `openrouter` | translating | completed | 11 |
| `openrouter` | refining | completed | 28 |
| `openrouter` | refining | failed | 1 |
| `openrouter` | formatting | completed | 11 |
| `openrouter_reasoning` | qa | completed | 11 |
| `qwen` | qa | completed | 1 |
| `local_recovery` | refining | completed | 5 |
| `local` | sentinel | completed | 31 |
| `local` | sentinel | failed | 1 |
| `local` | qa | hard_fail | 2 |

### Deterministic output checks

| Check | Result |
|---|---|
| Han Chinese body text | none found |
| Provider/meta leakage | none found |
| Quote-only lines | `0` |
| Final experiment outputs | all 10 exist |

## 5. ปัญหา อุปสรรค และการแก้ไข

ปัญหาที่พบ:

1. `ch131` หยุดจาก glossary coverage failure เพราะ `Containment Department` ถูกชนกับ alias ของ `Containment Sector`
   - แก้แล้วด้วย source-surface collision detection และ HGD alias cleanup
2. `ch184` หยุดจาก false glossary expectation เพราะ `Enter` match อยู่ใน `Entering` และมี semantic drift
   - แก้แล้วด้วย boundary-aware glossary subset matching และ rerun จาก stage ที่ปลอดภัย
3. `ch192` หยุดจาก peer-dialogue pronoun drift หลัง literal-safe omission recovery
   - แก้แล้วด้วย HGD-only peer-address repair หลัง recovery

ข้อจำกัดสำคัญ:

- แม้ output สุดท้ายสะอาด แต่ HGD OOS ยังไม่พิสูจน์ว่า pipeline พร้อมรันยาวแบบ unattended เพราะมี hard-fail/recovery หลายครั้ง
- มี QA record จาก `qwen` 1 ครั้งใน run นี้ ต้องนับเป็น routing evidence ในรายงาน OOS comparison

## 6. ข้อสรุปและก้าวต่อไป

ข้อสรุป: HGD OOS จบครบและ product-surface checks สะอาด แต่ long-run smoothness ยังมีความเสี่ยง เพราะต้องใช้หลาย treatment/recovery loop ระหว่างทาง

- Metric ด้าน final quality ดีขึ้น: ทุก chapter มี Sentinel `0/0/0/0`
- Metric ด้าน smoothness ยังไม่ดีพอ: มี hard-fail, local recovery, และ provider fallback evidence
- HGD OOS ให้หลักฐานสำคัญสำหรับ M6.3/M6.4 ว่า treatment ช่วยคุณภาพ output ได้ แต่ยังต้องระวังการ scale แบบ unattended

ก้าวต่อไป:

1. เดิน DSE OOS ต่อใน experiment vault ตาม sample ที่ล็อกไว้
2. หลัง DSE OOS จบหรือหยุด ให้เขียน research log แยกทันที
3. ต่อด้วย IRS OOS แล้วจึงทำ M6 comparison/recommendation
4. หลัง V6.34/M1-M7 เสร็จ ค่อยเริ่ม production request ใหม่: แปล DSE ต่อให้จบที่ `ch210` โดยตรวจ range ก่อนเริ่ม

