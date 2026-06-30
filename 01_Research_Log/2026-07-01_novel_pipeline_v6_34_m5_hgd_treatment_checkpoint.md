# บันทึกการวิจัย: V6.34 M5 HGD Treatment Checkpoint ch024-ch037

## 1. ข้อมูลพื้นฐาน

- Timestamp UTC: `2026-07-01T00:00:00Z`
- โครงการ: Novel Translation Pipeline
- หัวข้อ: V6.34 M5 HGD treatment checkpoint
- ผู้บันทึก: Codex
- สถานะ: checkpoint ผ่าน
- Artifact หลัก:
  - `07_Reports/v6_34_m5_hgd_treatment_checkpoint_ch024_ch037_20260701.md`
  - `Horror Game Developers/04_Work/_experiments/v6_34_m5_hgd_treatment_v1/07_Reports/sentinel_quality_v6-34-m5-hgd-treatment-v1_ch024_after_cleanup_20260630_231846.md`
  - `Horror Game Developers/04_Work/_experiments/v6_34_m5_hgd_treatment_v1/07_Reports/sentinel_quality_v6-34-m5-hgd-treatment-v1_ch037_sentinel_20260630_232230.md`

## 2. วัตถุประสงค์

รอบนี้ต้องการตรวจว่า treatment ที่เลือกสามารถพา HGD treatment run ผ่านจุดที่ baseline เคยหยุดได้หรือไม่

จุดวัดหลักคือ `ch024` ที่เจอ glossary parenthetical leakage และ `ch037` ที่ baseline เจอ title/glossary miss ของ `Velora Art Museum`

## 3. วิธีการและขั้นตอน

1. เพิ่ม deterministic cleanup สำหรับ pattern ปลอดภัย `thai_term (original/alias)`
2. เพิ่ม unit test ป้องกัน cleanup กว้างเกินไป
3. rerun `ch024-block-001` จาก formatting ใน treatment vault
4. รัน Sentinel เฉพาะ `ch024`
5. resume treatment ถึง `ch037`
6. ตรวจ H1/title sidecar และ Sentinel report ของ `ch037`

## 4. ผลการศึกษาและข้อมูลดิบ

| Item | Result |
|---|---|
| `ch024` after cleanup Sentinel | `0/0/0/0` |
| `ch037` Sentinel | `0/0/0/0` |
| `ch037` H1 | `# ตอนที่ 37 - พิพิธภัณฑ์ศิลปะเวโลรา [2]` |
| Current failed blocks | none |
| Pending treatment chapters | `ch066`, `ch103`, `ch132`, `ch142`, `ch170`, `ch196`, `ch225`, `ch250` |

## 5. ปัญหา อุปสรรค และการแก้ไข

ปัญหาใหม่คือ cleanup ทำให้ formatter validation มองว่า content changed เพราะ refined source ยังมี parenthetical English อยู่

การแก้คือใช้ source text ที่ผ่าน cleanup แบบเดียวกันเฉพาะตอน validate formatting output วิธีนี้ยังไม่ผ่อน validator กว้างๆ และยังจับ content drift อื่นได้เหมือนเดิม

## 6. ข้อสรุปและก้าวต่อไป

Treatment checkpoint ผ่าน: defect เดิมของ `ch037` หาย และ `ch024` glossary leakage ถูกแก้ด้วย deterministic cleanup ที่มี test

ก้าวต่อไปคือ continue M5 treatment rerun สำหรับ HGD in-sample ที่เหลือ แล้วค่อยสรุป metric movement ของ HGD treatment slice
