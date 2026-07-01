# บันทึกการวิจัย: V6.34 M6 OOS Scan And Glossary Gate

## 1. ข้อมูลพื้นฐาน

- Timestamp UTC: `2026-07-01T06:06:34Z`
- โครงการ: Novel Translation Pipeline
- หัวข้อ: V6.34 Milestone 6.1 out-of-sample scan and glossary gate
- ผู้บันทึก: Codex
- สถานะ: เสร็จสิ้น
- Artifact หลัก:
  - `07_Reports/v6_34_m6_oos_scan_glossary_gate_20260701.md`
  - `Deep Sea Embers/04_Work/_experiments/v6_34_m6_dse_oos_v1/07_Reports/v6_34_m6_oos_glossary_gate_decisions_v6-34-m6-dse-oos-v1.md`
  - `Horror Game Developers/04_Work/_experiments/v6_34_m6_hgd_oos_v1/07_Reports/v6_34_m6_oos_glossary_gate_decisions_v6-34-m6-hgd-oos-v1.md`
  - `Infinite Regressor Stories/04_Work/_experiments/v6_34_m6_irs_oos_v1/07_Reports/v6_34_m6_oos_glossary_gate_decisions_v6-34-m6-irs-oos-v1.md`

## 2. วัตถุประสงค์

รอบนี้ต้องเปิด Milestone 6 out-of-sample โดยไม่ทำให้ข้อมูล OOS กลายเป็นข้อมูล tuning ก่อนเริ่มแปลจริง จึงต้องตรวจ source parity, run scan-only, สร้าง decision report, และบันทึก `glossary_approved` records เพื่อให้ pipeline ไปต่อได้โดยยังใช้ glossary state เดิม

ความสำเร็จของรอบนี้คือทั้งสามนิยายมี experiment vault ที่ scan และ approve gate ครบถ้วน แต่ยังไม่มี translation/refinement/QA/formatting/completed record และไม่มี production artifact หรือ MoonRead surface ถูกแตะ

## 3. วิธีการและขั้นตอน

1. ตรวจ source parity ของ experiment vault เทียบกับ production `03_Raw/` สำหรับ OOS chapters ที่ล็อกไว้ใน manifest

```powershell
python scripts/verify_experiment_source_parity.py --novel-root "<novel root>" --experiment-root "<experiment vault>" --chapters "<locked OOS chapters>"
```

2. รัน scan-only gate ในแต่ละ experiment vault

```powershell
novel-pipeline --config ".system/config.yaml" run --range "<locked OOS chapters>" --run-id "<oos run id>" --stop-after glossary-scan
```

3. สร้าง glossary decision reports โดยอ่าน `04_Work/_batch/<run-id>/glossary_scan.json` ผ่าน key `items`

4. ใช้ OOS policy: ไม่ approve คำใหม่จาก OOS candidates และเก็บ candidates ทั้งหมดเป็น watchlist

5. Commit `glossary_approved` records ในแต่ละ experiment vault เพื่อเปิดทางให้ M6.2 แปลต่อจาก existing copied glossary state

```powershell
novel-pipeline --config ".system/config.yaml" approve-terms --run-id "<oos run id>" --batch --decision-report "<decision report>"
```

6. อ่าน `status --run-id` ของทั้งสาม run เพื่อยืนยันว่า stage หลัง approval ยังหยุดที่ translating pending

## 4. ผลการศึกษาและข้อมูลดิบ

### Source parity

| Novel | OOS chapters | Source parity |
|---|---|---:|
| Deep Sea Embers | 10 | 0 mismatches |
| Horror Game Developer | 10 | 0 mismatches |
| Infinite Regressor Stories | 10 | 0 mismatches |

### Scan and approval records

| Novel | Run ID | Candidate terms | Fetched | Scanned | Glossary approved | Translation/refine/QA/format/completed |
|---|---|---:|---:|---:|---:|---:|
| Deep Sea Embers | `v6-34-m6-dse-oos-v1` | 34 | 10 | 10 | 10 | 0 |
| Horror Game Developer | `v6-34-m6-hgd-oos-v1` | 17 | 10 | 10 | 10 | 0 |
| Infinite Regressor Stories | `v6-34-m6-irs-oos-v1` | 155 | 10 | 10 | 10 | 0 |

### Guardrail state

- Current failed blocks: `0` for all three OOS runs
- Historical failed records: `0` for all three OOS runs
- Next effective action: `resume --run-id <run-id>` for all three OOS runs
- Production glossary changes: none
- Production output changes: none
- MoonRead changes: none

## 5. ปัญหา อุปสรรค และการแก้ไข

### Candidate count report initially read the wrong JSON key

1. What happened: the first report-generation attempt read `candidates`, but `glossary_scan.json` stores scan records under `items`
2. How it was resolved: regenerated decision reports using `items`, with fallback handling for `term` / `original_term`
3. Outcome after resolution: decision reports show the expected counts: DSE `34`, HGD `17`, IRS `155`

### OOS candidates were not approved as new glossary terms

1. What happened: scan found many candidates, especially IRS with `155` candidates
2. How it was resolved: held all candidates as OOS watchlist and approved the batch gate with existing copied glossary state only
3. Outcome after resolution: OOS remains a valid generalization test instead of a tuning round

### ข้อจำกัดสำคัญ

- M6.1 does not measure translation quality yet because no OOS translation has run
- IRS still needs experiment-local title sidecar preparation before M6.2 because several OOS chapters did not have production `title.json` files when the vault was copied

## 6. ข้อสรุปและก้าวต่อไป

ข้อสรุป: M6.1 ผ่านในฐานะ scan/glossary gate แบบ out-of-sample ที่ยังไม่ปน tuning และพร้อมเข้าสู่ M6.2 หลังเตรียม title sidecars ที่จำเป็น

- ทั้งสาม OOS vault มี source parity `0` mismatches
- scan-only และ glossary approval gate completed ครบทั้งสาม run
- ไม่มี translation/refinement/QA/formatting/completed records หลุดเข้ามาในรอบนี้
- การไม่ approve คำใหม่จาก OOS candidates ทำให้ผล M6.2 ยังวัด generalization ได้ตรงกว่า

ก้าวต่อไป:
1. สร้างหรือคัดลอก experiment-local IRS title sidecars สำหรับ OOS chapters ที่ยังขาด
2. รัน M6.2 OOS translation/refine/QA/format/Sentinel โดยไม่ tune mid-round
3. บันทึก failure ทุกอย่างเป็นข้อมูลก่อนตัดสินใจแก้หรือเปลี่ยน routing
