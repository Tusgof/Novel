# บันทึกการวิจัย: V6.34 M5 Cross-Novel Treatment Comparison

## 1. ข้อมูลพื้นฐาน

- Timestamp UTC: `2026-07-01T05:44:44Z`
- โครงการ: Novel Translation Pipeline
- หัวข้อ: V6.34 Milestone 5 cross-novel treatment comparison
- ผู้บันทึก: Codex
- สถานะ: เสร็จสิ้น
- Artifact หลัก:
  - `07_Reports/v6_34_m5_cross_novel_treatment_comparison_20260701.md`
  - `07_Reports/v6_34_m5_hgd_baseline_vs_treatment_comparison_20260701.md`
  - `07_Reports/v6_34_m5_dse_treatment_v2_completion_20260701.md`
  - `07_Reports/v6_34_m5_irs_treatment_completion_20260701.md`

## 2. วัตถุประสงค์

รอบนี้ต้องเทียบหลักฐาน treatment ของ HGD, DSE, และ IRS ว่าพอจะเปิด Milestone 6 out-of-sample ได้หรือยัง หรือควรทำ feedback-loop treatment เพิ่มก่อน

เกณฑ์ความสำเร็จคือมีตารางเทียบผลทั้งสามเรื่อง, แยก output-surface quality ออกจาก long-run smoothness, และตัดสินใจ next safe action จากหลักฐาน ไม่ใช่จากความรู้สึก

## 3. วิธีการและขั้นตอน

1. อ่านรายงาน treatment/comparison ของทั้งสามเรื่อง
2. ดึง metric สำคัญ: completed blocks, current failed blocks, Sentinel result, source parity, provider failures, QA hard-fails, recovery events
3. จัด defect ตาม layer: multi-novel, language-level, novel-specific, run-local
4. ตัดสินว่าควรเปิด OOS ทันทีหรือเพิ่ม treatment rule ก่อน

รายงานอ้างอิง:

```powershell
Get-Content -Raw -Encoding UTF8 07_Reports/v6_34_m5_hgd_baseline_vs_treatment_comparison_20260701.md
Get-Content -Raw -Encoding UTF8 07_Reports/v6_34_m5_dse_treatment_v2_completion_20260701.md
Get-Content -Raw -Encoding UTF8 07_Reports/v6_34_m5_irs_treatment_completion_20260701.md
```

## 4. ผลการศึกษาและข้อมูลดิบ

| Novel | In-Sample Chapters | Blocks Complete | Current Failed | Final Sentinel | Key Risk |
|---|---:|---:|---:|---|---|
| HGD | 10 | 10/10 single-block chapters | 0 | 0/0/0/0 | QA hard-fails and omission recoveries |
| DSE | 10 | 56/56 | 0 | 0/0/0/0 | one recovered empty OpenRouter assistant |
| IRS | 10 | 32/32 | 0 | 0/0/1/0 | CJK/Hanja parenthetical leakage and one minor glossary miss |

ผลที่ดี:

- ทั้งสามเรื่องจบ treatment in-sample โดยไม่มี current failed block
- ไม่มี Sentinel blocker/major ใน final treatment result
- Source parity gate ป้องกัน DSE stale/off-by-one experiment vault ได้จริง
- IRS empty `Footnotes:` blocker ถูกแก้และไม่กลับมาใน final treatment

ผลที่ยังไม่ผ่านเต็มที่:

- HGD ยังต้องใช้ recovery หลายครั้ง
- IRS ยังเกิด QA hard-fail สองครั้งจาก CJK/Hanja parenthetical leakage
- Provider empty/mojibake output ยังเกิดขึ้นใน DSE/IRS
- IRS ยังมี minor glossary coverage miss หนึ่งรายการ

## 5. ปัญหา อุปสรรค และการแก้ไข

1. การแยก quality pass กับ smoothness pass
   - อาการ: ถ้าดูแค่ current failed = 0 จะเหมือนทุกอย่างดีแล้ว
   - การแก้: แยกตาราง output-surface quality และ long-run smoothness
   - ผลลัพธ์: เห็นว่าควรทำ pre-OOS hardening เล็กหนึ่งจุดก่อน M6

2. CJK/Hanja parenthetical leakage
   - อาการ: IRS hard-fail สองครั้งแม้ final output สะอาดหลัง rerun
   - การแก้ในรอบนี้: บันทึกเป็น Layer 1 candidate ไม่ใช่แก้เงียบ
   - ผลลัพธ์: next safe action ชัดเจนว่าต้องเพิ่ม rule แคบก่อน OOS

ข้อจำกัดสำคัญ: รอบนี้เป็นการเทียบรายงาน ไม่ใช่ provider rerun ใหม่ ตัวเลขจึงอ้างอิงจากรายงานและ ledger/status ที่บันทึกไว้ในแต่ละ treatment run

## 6. ข้อสรุปและก้าวต่อไป

ข้อสรุป: M5 treatment ผ่านด้าน output-surface แต่ยังควรทำ pre-OOS hardening เล็กสำหรับ CJK/Hanja parenthetical leakage ก่อนเปิด M6

- การแก้ที่ทำไปช่วยให้ HGD/DSE/IRS ไม่มี blocker/major ใน final treatment
- ความลื่นของการรันยาวยังไม่พอ เพราะยังมี QA hard-fail/recovery/provider malformed output
- CJK/Hanja parenthetical leakage เป็น repeated IRS in-sample defect ที่แก้ได้ด้วย rule แคบและมีโอกาสลด manual recovery ใน OOS

ก้าวต่อไป:

1. เพิ่ม narrow non-CJK parenthetical annotation cleanup/guard พร้อม test
2. รัน verification commands
3. อัปเดต docs ว่า pre-OOS hardening เสร็จหรือไม่
4. เปิด Milestone 6 OOS หลัง rule นี้ผ่านเท่านั้น
