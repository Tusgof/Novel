# บันทึกการวิจัย: V6.34C IRS Glossary Classification

## 1. ข้อมูลพื้นฐาน

- Timestamp UTC: `2026-06-30T20:50:44Z`
- โครงการ: Novel Translation Pipeline
- หัวข้อ: V6.34C IRS glossary classification after scan-only gate
- ผู้บันทึก: Codex
- สถานะ: เสร็จสิ้นสำหรับ classification; ยังไม่ commit glossary approval
- Artifact หลัก:
  - `07_Reports/v6_34c_irs_glossary_classification_20260701.md`
  - `Infinite Regressor Stories/04_Work/_experiments/v6_34c_irs_insample_v1/04_Work/_batch/v6-34c-irs-insample-v1/glossary_scan.json`

## 2. วัตถุประสงค์

รอบนี้จำแนก candidate terms 175 รายการจาก V6.34C IRS scan-only gate เพื่อหาว่าส่วนไหนพร้อม approve, ส่วนไหนควร map เป็น alias ของ glossary เดิม, ส่วนไหนควร reject, และส่วนไหนต้องใช้ source-aware review ก่อนอนุมัติ

ความสำเร็จของรอบนี้คือได้ classification ที่ทำให้ขั้นต่อไปปลอดภัยขึ้น โดยไม่รีบเพิ่ม glossary note ที่อาจผิดและไม่ resume translation ก่อน glossary gate พร้อม

## 3. วิธีการและขั้นตอน

1. อ่าน `glossary_scan.json` จาก experiment vault
2. ตรวจจำนวน candidate, category, chapter distribution และ exact match กับ IRS production glossary
3. จำแนก candidate เป็น 4 กลุ่ม:
   - approve-new candidate
   - alias-to-existing candidate
   - reject/noise candidate
   - ask-human/source-aware candidate
4. สร้าง report:

```powershell
07_Reports/v6_34c_irs_glossary_classification_20260701.md
```

5. ไม่สร้าง glossary notes และไม่ append `glossary_approved` ledger records ในรอบนี้ เพราะยังมี terms ที่ต้อง source-aware review

## 4. ผลการศึกษาและข้อมูลดิบ

| Class | Count |
|---|---:|
| Approve-new candidate | 62 |
| Alias-to-existing candidate | 19 |
| Reject/noise candidate | 41 |
| Ask-human/source-aware candidate | 53 |
| Total | 175 |

Key observations:

- `existing_exact_count` against production IRS glossary was `0`, but many candidates are variants or aliases of existing notes.
- Scanner captured useful late-range terms such as `Outer God`, `Regression Alliance`, `Monster Wave`, `Eastern Holy State`, and `True Dictator Club`.
- Scanner also captured clear noise such as `The Sage II This`, `YES Are`, `YES Ever`, `The Nurturer Today`, and title fragments with Roman numerals.
- Embedded CJK terms are a major IRS-specific pressure point in English-source chapters; approving them blindly could harm translation consistency.

## 5. ปัญหา อุปสรรค และการแก้ไข

1. Symptom: 175 candidates include mixed-quality data, including title/prose fragments and embedded CJK.
   - Action: split classification into four groups instead of treating all candidates as approval candidates.
   - Outcome: approval is now bounded to a smaller safe list, while ambiguous CJK/source artifacts are held for source-aware review.

2. Symptom: exact-match check found no existing glossary notes, even though many concepts already exist as aliases or canonical notes.
   - Action: created an alias-to-existing list in the classification report.
   - Outcome: next approval step can update aliases instead of duplicating terms.

3. Symptom: approving CJK terms in an English-source novel needs context, because some are literal source text, some are proper nouns, and some are concept aliases.
   - Action: held 53 terms in ask-human/source-aware state.
   - Outcome: no potentially harmful glossary notes were committed in this round.

ข้อจำกัดสำคัญ:

- This round is classification only. It does not create experiment-local glossary approval records.
- Translation treatment remains blocked by missing experiment-local `glossary_approved` records.

## 6. ข้อสรุปและก้าวต่อไป

ข้อสรุป: Classification is complete, but glossary approval should not be executed until the 53 source-aware candidates are reviewed.

- The scan result is useful but too noisy for automatic approval.
- Alias-to-existing handling should become a multi-novel glossary-pipeline improvement.
- Embedded CJK in English-source IRS should be treated as a novel/language pressure point.

ก้าวต่อไป:

1. Review the 53 ask-human/source-aware terms with source context.
2. Convert approved CJK/ambiguous terms into experiment-local notes or aliases.
3. Append experiment-local `glossary_approved` records for the 10 IRS chapters.
4. Resume `v6-34c-irs-insample-v1` translation only after approval records exist.

