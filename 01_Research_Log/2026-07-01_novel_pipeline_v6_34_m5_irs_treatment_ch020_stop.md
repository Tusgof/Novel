# บันทึกการวิจัย: V6.34 M5 IRS Treatment Stop at ch020

## 1. ข้อมูลพื้นฐาน

- Timestamp UTC: `2026-07-01T04:12:00Z`
- โครงการ: Novel Translation Pipeline
- หัวข้อ: IRS treatment measurement stopped by glossary note leakage at ch020
- ผู้บันทึก: Codex
- สถานะ: ยกเลิกระหว่างทาง
- Artifact หลัก:
  - `07_Reports/v6_34_m5_irs_treatment_ch020_stop_20260701.md`
  - `Infinite Regressor Stories/04_Work/_experiments/v6_34_m5_irs_treatment_v1/`
  - `Infinite Regressor Stories/04_Work/_experiments/v6_34_m5_irs_treatment_v1/07_Reports/sentinel_quality_v6-34-m5-irs-treatment-v1_ch020_manual_sentinel_20260701_040809.md`

## 2. วัตถุประสงค์

รอบนี้เริ่ม IRS treatment measurement สำหรับ official V6.34 in-sample sample หลังจาก HGD และ DSE treatment มีหลักฐานแล้ว เป้าหมายคือดูว่า treatment set เดิมรับ IRS ซึ่งเป็น stress target ได้หรือไม่ โดยยังไม่แตะ production output หรือ MoonRead

ความสำเร็จของรอบนี้คือ run ต้องผ่านอย่างน้อย sampled chapters โดยมี source parity ถูกต้อง, glossary gate ครบ, current failed blocks เป็นศูนย์, และ Sentinel blocker/major เป็นศูนย์

## 3. วิธีการและขั้นตอน

1. สร้าง isolated experiment vault:

```powershell
Infinite Regressor Stories/04_Work/_experiments/v6_34_m5_irs_treatment_v1
```

2. Copy runtime/config/glossary/profile/prompts/scripts จาก IRS production vault และ copy raw source เฉพาะ official in-sample chapters:

```text
ch020,ch067,ch080,ch119,ch160,ch207,ch261,ch276,ch322,ch361
```

3. ตรวจ source parity:

```powershell
python scripts/verify_experiment_source_parity.py --novel-root "Infinite Regressor Stories" --experiment-root "Infinite Regressor Stories/04_Work/_experiments/v6_34_m5_irs_treatment_v1" --chapters "ch020,ch067,ch080,ch119,ch160,ch207,ch261,ch276,ch322,ch361"
```

4. รัน scan-only gate:

```powershell
novel-pipeline --config ".system/config.yaml" run --range "ch020,ch067,ch080,ch119,ch160,ch207,ch261,ch276,ch322,ch361" --run-id v6-34-m5-irs-treatment-v1 --stop-after glossary-scan
```

5. สร้าง decision report ใน experiment vault โดย hold/reject all 119 new candidates และ approve new terms 0

6. commit glossary approval records:

```powershell
novel-pipeline --config ".system/config.yaml" approve-terms --run-id v6-34-m5-irs-treatment-v1 --batch --decision-report "07_Reports/v6_34_m5_irs_treatment_glossary_gate_decisions_20260701.md"
```

7. รัน bounded resume ถึง `ch020`:

```powershell
novel-pipeline --config ".system/config.yaml" resume --run-id v6-34-m5-irs-treatment-v1 --until-chapter ch020 --manual-action-mode stop
```

8. พบว่า IRS experiment config ไม่มี runtime Sentinel จึง patch เฉพาะ experiment vault แล้วรัน manual Sentinel สำหรับ `ch020`

## 4. ผลการศึกษาและข้อมูลดิบ

### ผลที่ดี

| Metric | Result |
|---|---:|
| Source parity mismatches | 0 |
| Scan candidates | 119 |
| Glossary approved ledger records | 10/10 |
| ch020 completed blocks | 4/4 |
| Current failed blocks after ch020 | 0 |
| Historical failed records after ch020 | 0 |

### ผลที่ยังไม่ผ่าน

| Metric | Result |
|---|---|
| ch020 Sentinel | blocker/major/minor/info `1/0/0/0` |
| Safe to publish | no |
| Blocker category | `glossary_note_leakage` |
| Evidence | `ดังซอริน: ชื่อตัวละคร` |

### Raw cause evidence

The source ends with an empty marker:

```text
Footnotes:
```

The generated literal/refined/final output invented glossary/category entries under Thai `เชิงอรรถ:` even though the source did not contain those entries.

## 5. ปัญหา อุปสรรค และการแก้ไข

1. ปัญหา: IRS experiment config copy did not include runtime Sentinel blocking.
   - การแก้ไข: patch เฉพาะ experiment vault เพื่อเพิ่ม `execution.sentinel.mode: blocking` และ copy Sentinel scripts into the vault.
   - ผลลัพธ์: manual Sentinel could run against vault-local output and found the true blocker.

2. ปัญหา: empty source `Footnotes:` marker caused provider to invent glossary/category notes.
   - การแก้ไข: ยังไม่แก้ในรอบนี้ เพราะต้องหยุดและบันทึก evidence ก่อนตาม experiment protocol.
   - ผลลัพธ์: treatment measurement stopped at `ch020`; no further chapters were processed.

## 6. ข้อสรุปและก้าวต่อไป

ข้อสรุป: IRS treatment measurement found a real blocker at the first sampled chapter, so the current treatment is not safe to continue without a small prevention step.

- Sentinel gate worked once pointed at the experiment vault.
- The defect is not a normal translation quality preference; it is glossary metadata leaking into product text.
- The most likely low-risk prevention is to strip or neutralize empty trailing `Footnotes:` source markers and ensure runtime Sentinel is enabled before IRS treatment resumes.

ก้าวต่อไป:
1. Implement the smallest prevention for empty `Footnotes:` marker leakage.
2. Ensure IRS experiment/production config carries blocking Sentinel before long runs.
3. Rerun `ch020` from the earliest affected stage in the same experiment vault.
4. If `ch020` passes Sentinel, continue IRS treatment one chapter at a time.
