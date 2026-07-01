# บันทึกการวิจัย: V6.34 M6 DSE OOS completion

## 1. ข้อมูลพื้นฐาน

- Timestamp UTC: `2026-07-01T12:29:05Z`
- โครงการ: Novel Translation Pipeline
- หัวข้อ: DSE out-of-sample completion after vault rebuild and output guardrail repair
- ผู้บันทึก: Codex
- สถานะ: เสร็จสิ้น
- Artifact หลัก:
  - `07_Reports/v6_34_m6_dse_oos_completion_20260701.md`
  - `Deep Sea Embers/04_Work/_experiments/v6_34_m6_dse_oos_v2/06_Logs/run_ledger.jsonl`
  - `Deep Sea Embers/04_Work/_experiments/v6_34_m6_dse_oos_v2/05_Output/`
  - `07_Reports/sentinel_quality_v6-34-m6-dse-oos-v2_*`

## 2. วัตถุประสงค์

รอบนี้ต้องทำ DSE out-of-sample ให้จบหลังจาก v1 ถูกยกเลิกเพราะ source parity ผิด โดยต้องใช้ experiment vault ที่ rebuild จาก production raw/title sidecars ปัจจุบัน

ความสำเร็จคือ DSE OOS ต้องครบ 10 sampled chapters, source parity เป็นศูนย์, current failed blocks เป็นศูนย์, output guardrails ผ่าน, Sentinel ผ่านทุก chapter, และไม่แตะ production/MoonRead

## 3. วิธีการและขั้นตอน

1. สร้าง `v6_34_m6_dse_oos_v2` ใหม่จาก production DSE:
   - config/glossary/prompts/scripts/profile
   - `03_Raw` เฉพาะ locked OOS chapters
   - `04_Work/<chapter>/title.json` เฉพาะ locked OOS chapters
2. ตรวจ source parity:

```powershell
python scripts\verify_experiment_source_parity.py --novel-root "Deep Sea Embers" --experiment-root "Deep Sea Embers\04_Work\_experiments\v6_34_m6_dse_oos_v2" --chapters "ch009,ch029,ch047,ch070,ch088,ch095,ch124,ch143,ch148,ch174"
```

3. รัน scan-only และ commit `glossary_approved` แบบ no-new-OOS-terms
4. Resume OOS translation/refine/QA/format/Sentinel ด้วย `--manual-action-mode stop`
5. เมื่อ `ch029-block-005` hard-fail จาก Chinese annotation leakage ให้เพิ่ม output-side cleanup และ rerun จาก refine
6. เมื่อ final output guardrail เจอ duplicate title-like body paragraph ใน `ch174` ให้ขยาย final assembly cleanup และ rerun final assembly
7. รัน final verification:

```powershell
python -m compileall novel_pipeline
$env:PYTHONIOENCODING='utf-8'
python test_translation.py
python scripts\check_output_quality_guardrails.py --chapters ch009,ch029,ch047,ch070,ch088,ch095,ch124,ch143,ch148,ch174
novel-pipeline --config ".system/config.yaml" status --run-id v6-34-m6-dse-oos-v2
```

## 4. ผลการศึกษาและข้อมูลดิบ

| Metric | Result |
|---|---:|
| Sampled chapters | 10 |
| Completed blocks | 55/55 |
| Current failed blocks | 0 |
| Historical failed records | 1 |
| Manual actions needed | 0 |
| Source parity mismatches | 0 |
| Output guardrail result | passed |
| Final outputs | 10/10 exist |

### Chapter completion

| Chapter | Blocks | Output |
|---|---:|---|
| `ch009` | 6/6 | exists |
| `ch029` | 5/5 | exists |
| `ch047` | 5/5 | exists |
| `ch070` | 5/5 | exists |
| `ch088` | 6/6 | exists |
| `ch095` | 5/5 | exists |
| `ch124` | 6/6 | exists |
| `ch143` | 5/5 | exists |
| `ch148` | 6/6 | exists |
| `ch174` | 6/6 | exists |

### Provider evidence

| Provider | Stage evidence |
|---|---|
| `openrouter` | translating/refining/formatting and some QA fallback completions |
| `openrouter_reasoning` | main QA completions |
| `local_recovery` | 2 refinement recovery records |
| `local` | fetched/glossary gates/completed/sentinel; 1 historical QA hard_fail |

## 5. ปัญหา อุปสรรค และการแก้ไข

1. **อาการ:** DSE OOS v1 ใช้ raw source stale/off-by-one
   - **การแก้ไข:** ยกเลิก v1, rebuild v2 จาก production raw/title sidecars, verify source parity 0
   - **ผลลัพธ์:** v2 เป็น valid measurement vault

2. **อาการ:** `ch029-block-005` hard-fail เพราะ `[走进不科学]` หลุดใน output
   - **การแก้ไข:** เพิ่ม `_apply_source_script_annotation_repairs()`
   - **ผลลัพธ์:** rerun ผ่าน QA และ output ไม่มี Han Chinese

3. **อาการ:** `ch174` final output มี hallucinated duplicate title paragraph
   - **การแก้ไข:** ขยาย `_remove_duplicate_title_paragraph()` ให้ลบ standalone title-like paragraphs ทุกตำแหน่งเมื่อ H1 เป็น authoritative title
   - **ผลลัพธ์:** rerun final assembly แล้ว output guardrails ผ่าน

ข้อจำกัดสำคัญ:

- DSE OOS ยังไม่ใช่ production output และห้าม publish ไป MoonRead
- DSE OOS สำเร็จด้าน output surface แต่ยังมี evidence ว่ารันยาวต้อง monitor เพราะมี retry/fallback/recovery หลายครั้ง

## 6. ข้อสรุปและก้าวต่อไป

ข้อสรุป: DSE OOS v2 ผ่านครบ 10 sampled chapters หลังแก้ source parity, source-script leakage, และ duplicate-title paragraph prevention

- วัดผลได้ว่า source parity gate จำเป็นจริง เพราะ v1 ผิดทั้ง 10 chapters
- output guardrail มีประโยชน์จริง เพราะจับ duplicate title ที่ provider QA/Sentinel ปล่อยผ่าน
- source-script annotation cleanup เป็น low-effort/high-impact guard ที่ลด Han leakage ได้โดยไม่ลดคุณภาพการแปล

ก้าวต่อไป:

1. Commit/push DSE OOS completion evidence and code cleanup
2. เปิด IRS OOS ใน isolated experiment vault ด้วย source parity/title readiness check ก่อน provider calls
3. หลัง IRS OOS จบ ให้ทำ M6 comparison/recommendation รวม HGD + DSE + IRS
