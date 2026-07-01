# บันทึกการวิจัย: V6.34 M6 ch184 Treatment Implementation

## 1. ข้อมูลพื้นฐาน

- Timestamp UTC: `2026-07-01T07:44:54Z`
- โครงการ: Novel Translation Pipeline
- หัวข้อ: V6.34 M6 treatment for HGD ch184 QA hard-fail
- ผู้บันทึก: Codex
- สถานะ: เสร็จสิ้น
- Artifact หลัก:
  - `07_Reports/v6_34_m6_ch184_treatment_implementation_20260701.md`
  - `Horror Game Developers/04_Work/_experiments/v6_34_m6_hgd_oos_v1/07_Reports/sentinel_quality_v6-34-m6-hgd-oos-v1_ch184_sentinel_20260701_074411.json`

## 2. วัตถุประสงค์

รอบนี้ implement treatment จาก ch184 analysis เพื่อแก้ false glossary expectation ที่เกิดจาก `Enter` match ใน `Entering` และ rerun block โดยไม่ force-accept

ความสำเร็จคือ resolver ต้องไม่ส่ง `Enter` เข้า glossary subset เมื่อ source มีแค่ `Entering`, tests ต้องผ่าน, และ `ch184` ต้องผ่าน QA/Sentinel พร้อม spot-check จุด semantic drift เดิม

## 3. วิธีการและขั้นตอน

1. เพิ่ม `_source_key_occurrences()` ใน `novel_pipeline/pipeline.py`
2. เปลี่ยน `_resolve_glossary_subset()` ให้ใช้ boundary-aware regex สำหรับ source keys ที่มี alphabetic characters
3. เพิ่ม regression test ใน `test_translation.py`
4. รัน validation

```powershell
cd "D:\Fogust\Workspace\Novel\Deep Sea Embers"
$env:PYTHONIOENCODING='utf-8'
python -m compileall novel_pipeline
python test_translation.py
```

5. Rerun `ch184-block-001` from `refine`
6. Spot-check พบ semantic drift เดิมยังอยู่ แม้ QA/Sentinel ผ่าน
7. Rerun `ch184-block-001` from `translate`

```powershell
cd "D:\Fogust\Workspace\Novel\Horror Game Developers\04_Work\_experiments\v6_34_m6_hgd_oos_v1"
$env:PYTHONIOENCODING='utf-8'
novel-pipeline --config ".system/config.yaml" rerun-block --run-id v6-34-m6-hgd-oos-v1 --block-id ch184-block-001 --from-stage translate
```

8. Verify latest QA, Sentinel, and output text

## 4. ผลการศึกษาและข้อมูลดิบ

### Validation

| Check | Result |
|---|---|
| compileall | pass |
| test_translation.py | pass |
| git diff --check | pass |
| rerun from refine | pipeline pass, human spot-check fail |
| rerun from translate | pass |
| latest QA | pass, retry `0` |
| latest Sentinel | `0/0/0/0` |

### Output spot check

| Check | Result |
|---|---|
| `สะกดรอยตาม` remains | no |
| false `ปุ่ม Enter` remains | no |
| relevant thought | `เป็นไปได้ไหมว่าเขาสังเกตเห็นอยู่คนเดียว?` |

## 5. ปัญหา อุปสรรค และการแก้ไข

### First rerun from refine false-passed

1. What happened: QA/Sentinel passed, but manual spot-check still found semantic drift
2. How it was resolved: reran from `translate` to regenerate literal/refine path
3. Outcome after resolution: QA passed retry `0`, Sentinel `0/0/0/0`, and spot-check passed

### Glossary matching bug fixed

1. What happened: `Enter` could match inside `Entering`
2. How it was resolved: added boundary-aware matching for alphabetic source keys
3. Outcome after resolution: regression test proves `Enter` does not match `Entering`, while `[Enter]` still matches

## 6. ข้อสรุปและก้าวต่อไป

ข้อสรุป: ch184 treatment worked, but it also proves recovered risky blocks need a narrow human/Codex spot-check because QA/Sentinel can false-pass semantic drift

- Layer 0 glossary subset bug is fixed and tested
- `ch184` is no longer current failed
- HGD OOS can resume from `ch192`

ก้าวต่อไป:
1. Commit and push the treatment
2. Resume HGD OOS from `ch192`
3. Continue stopping on provider failure, QA hard-fail, or Sentinel blocker/major
