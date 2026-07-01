# บันทึกการวิจัย: V6.34 M5 IRS Empty Footnote Marker Prevention

## 1. ข้อมูลพื้นฐาน

- Timestamp UTC: `2026-07-01T04:17:00Z`
- โครงการ: Novel Translation Pipeline
- หัวข้อ: Prevent empty IRS Footnotes marker from causing glossary note leakage
- ผู้บันทึก: Codex
- สถานะ: เสร็จสิ้น
- Artifact หลัก:
  - `07_Reports/v6_34_m5_irs_footnote_marker_prevention_20260701.md`
  - `Deep Sea Embers/novel_pipeline/text_utils.py`
  - `Deep Sea Embers/test_translation.py`
  - `Infinite Regressor Stories/.system/config.yaml`

## 2. วัตถุประสงค์

รอบนี้ต้องแก้ blocker ที่พบใน IRS treatment `ch020` ด้วยวิธีที่ effort ต่ำและไม่ลดคุณภาพการแปล โดยไม่แก้แบบ manual patch ที่ final output เท่านั้น

ความสำเร็จคือ provider prompts ต้องไม่เห็น empty trailing `Footnotes:` marker ที่ชวนให้โมเดลแต่งเชิงอรรถเอง แต่กรณี source มี footnote marker จริงเช่น `[1]` ต้องยังคงอยู่

## 3. วิธีการและขั้นตอน

1. เพิ่ม source normalizer ใน `novel_pipeline.text_utils`:
   - `strip_empty_trailing_footnote_marker(text, source_language)`
   - ใช้กับ non-CJK source เท่านั้น
   - ลบเฉพาะ bare trailing `Footnotes:`
2. ต่อ normalizer เข้า `split_blocks()` ก่อนสร้าง block ให้ provider
3. เพิ่ม regression test:

```powershell
python test_translation.py
```

4. เพิ่ม blocking Sentinel config ให้ IRS production config เพื่อให้ experiment copy รอบถัดไปไม่ขาด runtime Sentinel
5. พิสูจน์ใน experiment vault โดย rerun block ที่เสีย:

```powershell
novel-pipeline --config ".system/config.yaml" rerun-block --run-id v6-34-m5-irs-treatment-v1 --block-id ch020-block-004 --from-stage translate
```

## 4. ผลการศึกษาและข้อมูลดิบ

| Metric | Result |
|---|---|
| compileall | passed |
| test_translation.py | passed |
| ch020-block-004 rerun | completed |
| QA retry after fix | 0 |
| Latest runtime Sentinel for ch020 | `0/0/0/0` |
| Current failed blocks | none |

Latest Sentinel evidence:

```text
Safe to publish: yes
Blocker/Major/Minor/Info: 0/0/0/0
```

Report path:

```text
Infinite Regressor Stories/04_Work/_experiments/v6_34_m5_irs_treatment_v1/07_Reports/sentinel_quality_v6-34-m5-irs-treatment-v1_ch020_sentinel_20260701_041436.md
```

## 5. ปัญหา อุปสรรค และการแก้ไข

1. ปัญหา: IRS config เดิมไม่มี runtime Sentinel section
   - การแก้ไข: เพิ่ม `execution.sentinel.mode: blocking` และ `fail_on: major` ใน IRS production config
   - ผลลัพธ์: experiment/runtime gate สามารถสร้าง Sentinel ledger/report ได้หลัง rerun

2. ปัญหา: ต้องไม่ลบ source footnote จริง
   - การแก้ไข: test ครอบคลุมทั้ง empty `Footnotes:` และ real `Footnotes:\n[1]`
   - ผลลัพธ์: empty marker ถูกลบ แต่ real marker ยังอยู่

## 6. ข้อสรุปและก้าวต่อไป

ข้อสรุป: empty-footnote-marker prevention แก้ IRS `ch020` blocker ได้จริงและวัดผลได้ด้วย Sentinel `0/0/0/0`

- แก้ที่ source block ก่อน provider prompt ไม่ใช่ patch final output
- ขอบเขตแคบพอที่จะไม่กระทบ DSE/HGD หรือ footnote จริง
- Sentinel config parity ลดโอกาสที่ experiment vault จะพลาด gate แบบเดิม

ก้าวต่อไป:
1. Commit/push prevention และ research log
2. Continue IRS treatment measurement from `ch067`
3. Stop and log immediately if another Sentinel/provider/manual gate appears
