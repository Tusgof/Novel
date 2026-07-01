# บันทึกการวิจัย: V6.34 M6 ch131 Treatment Implementation

## 1. ข้อมูลพื้นฐาน

- Timestamp UTC: `2026-07-01T07:13:34Z`
- โครงการ: Novel Translation Pipeline
- หัวข้อ: V6.34 M6 treatment for HGD ch131 glossary conflict
- ผู้บันทึก: Codex
- สถานะ: เสร็จสิ้น
- Artifact หลัก:
  - `07_Reports/v6_34_m6_ch131_treatment_implementation_20260701.md`
  - `Horror Game Developers/04_Work/_experiments/v6_34_m6_hgd_oos_v1/07_Reports/sentinel_quality_v6-34-m6-hgd-oos-v1_ch131_sentinel_20260701_071217.json`

## 2. วัตถุประสงค์

รอบนี้นำ treatment ที่เลือกใน M6.3 มา implement เพื่อแก้ปัญหา HGD `ch131` โดยไม่ทำเป็น manual output patch และไม่ลดคุณภาพงานแปล

ความสำเร็จคือระบบต้องจับ glossary source-surface collision ได้ล่วงหน้า, HGD glossary ต้องไม่ขัดกันตรง `Containment Department`, และ rerun `ch131` ต้องผ่าน Sentinel

## 3. วิธีการและขั้นตอน

1. เพิ่ม section `Source Surface Collisions` ใน `build_glossary_conflicts_report()`
2. ให้ detector ตรวจ approved original terms และ aliases ทั้งหมด แล้ว flag เมื่อ source surface เดียวกัน map ไปหลาย approved notes ที่มี Thai term ต่างกัน
3. เพิ่ม regression test ใน `test_translation.py`
4. ลบ alias ที่ชนกันออกจาก `Horror Game Developers/01_Glossary/Containment Sector.md`
5. Copy glossary note ที่แก้แล้วเข้า HGD OOS experiment vault
6. รัน validation

```powershell
cd "D:\Fogust\Workspace\Novel\Deep Sea Embers"
$env:PYTHONIOENCODING='utf-8'
python -m compileall novel_pipeline
python test_translation.py
```

7. Rerun affected OOS block from refine

```powershell
cd "D:\Fogust\Workspace\Novel\Horror Game Developers\04_Work\_experiments\v6_34_m6_hgd_oos_v1"
$env:PYTHONIOENCODING='utf-8'
novel-pipeline --config ".system/config.yaml" rerun-block --run-id v6-34-m6-hgd-oos-v1 --block-id ch131-block-001 --from-stage refine
```

## 4. ผลการศึกษาและข้อมูลดิบ

### Validation

| Check | Result |
|---|---|
| compileall | pass |
| test_translation.py | pass |
| git diff --check | pass |
| ch131 rerun from refine | completed |
| ch131 QA | passed after retry 1 |
| latest ch131 Sentinel | `0/0/0/0` |

### HGD OOS state after treatment

| Metric | Value |
|---|---:|
| Completed OOS chapters | 5 |
| Current failed blocks | 0 |
| Historical failed records | 1 |
| Remaining pending chapters | 5 |

`ch131` output now uses `แผนกกักกัน` for `Containment Department`.

## 5. ปัญหา อุปสรรค และการแก้ไข

### QA needed one retry after rerun

1. What happened: rerun from refine failed QA once, then re-refined with feedback
2. How it was resolved: pipeline normal retry path completed
3. Outcome after resolution: QA passed retry 1, formatting completed, final chapter output rewritten, Sentinel passed

### New detector surfaces additional name/location collisions

1. What happened: after adding `Source Surface Collisions`, HGD glossary report also surfaces entries such as `Kaelen`, `Malovia Island`, `Sarah`, and `Serelith`
2. How it was resolved: no immediate cleanup in this treatment because those are not the `ch131` failure cause
3. Outcome after resolution: they remain visible follow-up glossary hygiene items

## 6. ข้อสรุปและก้าวต่อไป

ข้อสรุป: Treatment worked for the observed HGD `ch131` OOS glossary conflict and improved the glossary conflict detector for future novels

- Layer 0 detector now catches original/alias source-surface collisions with different Thai terms
- Layer 2 HGD glossary no longer maps `Containment Department` through `Containment Sector.md`
- `ch131` passes latest Sentinel `0/0/0/0`

ก้าวต่อไป:
1. Commit and push the treatment
2. Resume HGD OOS from the next pending chapter `ch153`
3. Continue recording OOS failures as data if another blocker/major appears
