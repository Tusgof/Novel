# บันทึกการวิจัย: V6.34 M5 Pre-OOS CJK/Hanja Parenthetical Hardening

## 1. ข้อมูลพื้นฐาน

- Timestamp UTC: `2026-07-01T05:51:51Z`
- โครงการ: Novel Translation Pipeline
- หัวข้อ: Pre-OOS CJK/Hanja parenthetical cleanup
- ผู้บันทึก: Codex
- สถานะ: เสร็จสิ้น
- Artifact หลัก:
  - `07_Reports/v6_34_m5_pre_oos_cjk_parenthetical_hardening_20260701.md`
  - `Deep Sea Embers/novel_pipeline/text_utils.py`
  - `Deep Sea Embers/test_translation.py`

## 2. วัตถุประสงค์

รอบนี้แก้ hardening item ที่เกิดจาก M5 cross-novel comparison: IRS มี QA hard-fail ซ้ำสองครั้งจาก Hanja/Han parenthetical annotation ใน non-CJK source แม้สุดท้ายจะ recovery ได้

เป้าหมายคือเพิ่ม rule แคบก่อน OOS เพื่อไม่ส่ง source-script annotation ที่ซ้ำความหมายอยู่แล้วเข้า provider prompt และลดโอกาส manual recovery ใน Milestone 6

## 3. วิธีการและขั้นตอน

1. อ่าน `text_utils.py` และพบว่ามี `normalize_embedded_cjk_glosses()` อยู่แล้ว แต่ครอบคลุมเฉพาะ CJK phrase ตามด้วย English gloss
2. เพิ่ม `normalize_quoted_cjk_meaning_terms()` สำหรับรูปแบบ quoted source-script term + `meaning ...`
3. เพิ่ม `strip_parenthetical_cjk_annotations()` สำหรับวงเล็บที่มีแต่ CJK/Hanja/Hangul/Kana annotation
4. ต่อ rule ทั้งสองเข้า `split_blocks()` สำหรับ non-CJK source เท่านั้น
5. เพิ่ม regression tests ใน `test_translation.py`
6. ทดสอบกับ raw IRS `ch080` และ `ch261`

คำสั่งตรวจหลัก:

```powershell
python -m compileall novel_pipeline
python test_translation.py
novel-pipeline --config ".system/config.yaml" preflight
```

## 4. ผลการศึกษาและข้อมูลดิบ

| Metric | Result |
|---|---:|
| targeted tests | pass |
| compileall | pass |
| full test_translation.py | pass |
| IRS ch080 source-script chars after split | 0 |
| IRS ch261 source-script chars after split | 0 |

Preflight result: degraded only because working tree was dirty before commit; provider readiness was OK

## 5. ปัญหา อุปสรรค และการแก้ไข

1. PowerShell heredoc syntax
   - อาการ: ใช้ bash `python - <<'PY'` แล้ว PowerShell parse ไม่ผ่าน
   - การแก้: เปลี่ยนเป็น PowerShell here-string pipe เข้า Python
   - ผลลัพธ์: targeted tests รันได้

2. Regex ไม่รองรับ comma ก่อนปิด quote
   - อาการ: pattern แรกไม่จับ `‘군주 (君主),’ meaning ...`
   - การแก้: ปรับ regex ให้ comma อยู่ก่อนหรือหลัง quote ได้
   - ผลลัพธ์: targeted tests และ raw IRS probe ผ่าน

ข้อจำกัดสำคัญ: rule นี้เป็น source-prompt normalization ไม่ใช่ proof ว่า OOS จะไม่มี leakage ต้องใช้ Milestone 6 OOS วัดผลจริง

## 6. ข้อสรุปและก้าวต่อไป

ข้อสรุป: pre-OOS hardening สำหรับ CJK/Hanja parenthetical annotation เสร็จและผ่าน regression แล้ว

- ลด source-script leakage risk ตั้งแต่ก่อนเรียก provider
- จำกัดเฉพาะ non-CJK source เพื่อไม่ทำลาย DSE/Chinese source
- Preserve normal English parentheses
- IRS ch080/ch261 raw probe เหลือ source-script chars หลัง split เป็น 0

ก้าวต่อไป:

1. Commit/push hardening log และ code
2. อัปเดต docs ให้ Next Safe Action เป็นเปิด Milestone 6 OOS
3. เริ่ม Milestone 6 OOS โดยใช้ locked out-of-sample chapters และห้าม tune กลางรอบ
