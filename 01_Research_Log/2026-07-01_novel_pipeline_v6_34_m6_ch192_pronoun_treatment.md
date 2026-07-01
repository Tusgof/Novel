# บันทึกการวิจัย: V6.34 M6 ch192 pronoun recovery treatment

## 1. ข้อมูลพื้นฐาน

- Timestamp UTC: `2026-07-01T08:15:03Z`
- โครงการ: Novel Translation Pipeline
- หัวข้อ: V6.34 M6 HGD ch192 pronoun treatment
- ผู้บันทึก: Codex
- สถานะ: เสร็จสิ้น
- Artifact หลัก:
  - `07_Reports/v6_34_m6_ch192_pronoun_treatment_implementation_20260701.md`
  - `Deep Sea Embers/novel_pipeline/pipeline.py`
  - `Deep Sea Embers/test_translation.py`
  - `Horror Game Developers/04_Work/_experiments/v6_34_m6_hgd_oos_v1/07_Reports/sentinel_quality_v6-34-m6-hgd-oos-v1_ch192_sentinel_20260701_081503.json`

## 2. วัตถุประสงค์

รอบนี้ต้องตอบว่า `ch192-block-001` ที่หยุดจาก QA pronoun drift ควรแก้ด้วยวิธีใดโดยไม่ลดคุณภาพการแปล และต้องป้องกันไม่ให้ literal-safe omission recovery สร้างปัญหา pronoun drift แบบเดียวกันซ้ำใน HGD

ความสำเร็จคือแก้เฉพาะจุดที่มีหลักฐาน, ไม่แทน `คุณ` แบบกว้างจนทำลายบริบท system/formal/`ขอบคุณ`, มี regression test, และ rerun `ch192` ผ่าน QA/Sentinel

## 3. วิธีการและขั้นตอน

1. อ่าน HGD pronoun policy และ artifact ของ `ch192-block-001`
2. ตรวจ root cause พบว่า refined artifact ใช้ `provider: local_recovery` และ `recovery_reason: qa_omission_literal_safe_refined_text`
3. เพิ่ม helper HGD-only ใน pipeline เพื่อซ่อม peer-address pattern หลัง literal-safe recovery
4. เพิ่ม regression test ว่า helper:
   - ทำงานเฉพาะ `novel_id: horror-game-developer`
   - แก้ peer-dialogue pattern ที่เจอ
   - ไม่ทำลายคำว่า `ขอบคุณ`
5. รัน compile/test

```powershell
cd "D:\Fogust\Workspace\Novel\Deep Sea Embers"
python -m compileall novel_pipeline
$env:PYTHONIOENCODING='utf-8'
python test_translation.py
```

6. rerun block จาก refine

```powershell
cd "D:\Fogust\Workspace\Novel\Horror Game Developers\04_Work\_experiments\v6_34_m6_hgd_oos_v1"
$env:PYTHONIOENCODING='utf-8'
novel-pipeline --config ".system/config.yaml" rerun-block --run-id v6-34-m6-hgd-oos-v1 --block-id ch192-block-001 --from-stage refine
```

7. ตรวจ status, QA artifact, Sentinel artifact, และ phrase counts

## 4. ผลการศึกษาและข้อมูลดิบ

### Test results

| Check | Result |
|---|---|
| `python -m compileall novel_pipeline` | passed |
| `PYTHONIOENCODING=utf-8 python test_translation.py` | passed |
| `ch192-block-001` rerun from refine | completed |
| QA | passed |
| Runtime Sentinel | `0/0/0/0` |

### ch192 status after treatment

| Metric | Value |
|---|---:|
| Completed HGD OOS chapters | `8/10` |
| Current failed blocks | `0` |
| Historical failed records | `4` |
| Pending chapters | `ch226`, `ch262` |

### Phrase spot-check

| Phrase | Count |
|---|---:|
| `ถ้าคุณมีอุปกรณ์อิเล็กทรอนิกส์` | 0 |
| `ถ้านายมีอุปกรณ์อิเล็กทรอนิกส์` | 1 |
| `คุณฉลาดไม่เบาเลยนะ` | 0 |
| `นายฉลาดไม่เบาเลยนะ` | 1 |
| `ขอบคุณ` | 1 |

## 5. ปัญหา อุปสรรค และการแก้ไข

ปัญหา:

1. Normal refine omitted major content, triggering literal-safe omission recovery.
2. Literal-safe recovery restored source coverage but did not apply HGD peer-address policy.
3. QA correctly blocked the result.

การแก้ไข:

- Added HGD-only targeted peer-address repair after literal-safe recovery.
- Avoided broad replacement so `ขอบคุณ` and system/formal `คุณ` contexts are not globally changed.
- Added regression coverage.

ผลหลังแก้:

- `ch192-block-001` passed QA and Sentinel.
- The known bad peer-address phrases were removed from final experiment output.
- No production output or MoonRead content was changed.

## 6. ข้อสรุปและก้าวต่อไป

ข้อสรุป: The treatment fixed the observed ch192 OOS pronoun failure with a narrow HGD-scoped recovery rule and did not reduce source coverage.

- This improves sustainable long-run operation because omission recovery no longer bypasses the known HGD peer-address policy for observed high-confidence patterns.
- It remains novel-specific; do not promote broad pronoun rewriting to Layer 0 without more cross-novel evidence.
- HGD OOS still needs to finish `ch226` and `ch262` before M6.2 can be called complete.

ก้าวต่อไป:

1. Resume HGD OOS from `ch226`.
2. Stop and log if another QA hard-fail, Sentinel blocker/major, provider failure, or scope expansion appears.
3. If HGD OOS completes, generate the HGD OOS completion report before moving to DSE/IRS OOS.

