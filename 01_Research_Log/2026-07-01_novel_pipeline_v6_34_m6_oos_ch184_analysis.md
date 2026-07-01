# บันทึกการวิจัย: V6.34 M6 ch184 Analysis

## 1. ข้อมูลพื้นฐาน

- Timestamp UTC: `2026-07-01T07:31:49Z`
- โครงการ: Novel Translation Pipeline
- หัวข้อ: V6.34 M6 analysis for HGD ch184 QA hard-fail
- ผู้บันทึก: Codex
- สถานะ: เสร็จสิ้น
- Artifact หลัก:
  - `07_Reports/v6_34_m6_oos_ch184_analysis_treatment_selection_20260701.md`
  - `Horror Game Developers/04_Work/_experiments/v6_34_m6_hgd_oos_v1/04_Work/ch184/ch184-block-001.qa.json`

## 2. วัตถุประสงค์

วิเคราะห์ QA hard-fail ของ HGD OOS `ch184-block-001` ก่อนแก้ เพื่อแยกว่าเป็นปัญหา pipeline ระดับ shared layer หรือเป็นแค่การ recovery เฉพาะ block

ความสำเร็จคือระบุ treatment ที่เล็กที่สุดและวัดผลได้ โดยไม่ force-accept และไม่ patch output ด้วยมือ

## 3. วิธีการและขั้นตอน

1. อ่าน QA artifact ของ `ch184-block-001`
2. ตรวจ source/literal/refined รอบจุดที่ QA ระบุ
3. ตรวจ `_resolve_glossary_subset()` ใน `novel_pipeline/pipeline.py`
4. จำแนก defect layer และเลือก treatment

## 4. ผลการศึกษาและข้อมูลดิบ

### Finding 1: false glossary expectation

| Item | Value |
|---|---|
| QA expected | `ปุ่ม Enter` |
| Source evidence | `Entering the orphanage, I closed the door behind me.` |
| Actual `[Enter]` source key | not present |
| Root cause | `_resolve_glossary_subset()` uses substring matching (`key in text`) |

### Finding 2: semantic drift

| Item | Value |
|---|---|
| Source intent | `Is it possible that he’s the only one who can see it?` |
| Bad refined phrase | `สะกดรอยตาม` |
| Classification | semantic drift during refinement |

## 5. ปัญหา อุปสรรค และการแก้ไข

### Glossary subset resolver is too permissive for alphabetic terms

1. What happened: `Enter` matched inside `Entering`
2. How it was resolved: not changed in this analysis step; selected treatment is boundary-aware matching
3. Outcome after resolution: next implementation step is clear and testable

### Semantic drift remains in refined output

1. What happened: refined text introduced `สะกดรอยตาม`
2. How it was resolved: no manual patch in this analysis step
3. Outcome after resolution: selected action is rerun from refine after glossary subset fix

## 6. ข้อสรุปและก้าวต่อไป

ข้อสรุป: `ch184` exposes one shared pipeline bug and one run-local semantic drift; the shared bug should be fixed before rerun

- Layer 0: glossary subset matching must use word boundaries for alphabetic source keys
- Layer 3: semantic drift can be handled by normal rerun/QA after false glossary pressure is removed

ก้าวต่อไป:
1. Implement boundary-aware source key matching in `_resolve_glossary_subset()`
2. Add regression test for `Enter` versus `Entering`
3. Rerun `ch184-block-001` from `refine`
