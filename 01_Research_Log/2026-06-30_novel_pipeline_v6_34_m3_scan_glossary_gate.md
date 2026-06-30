# บันทึกการวิจัย: V6.34 M3 Scan และ Glossary Gate สำหรับ Baseline

## 1. ข้อมูลพื้นฐาน

- Timestamp UTC: `2026-06-30T22:25:12Z`
- โครงการ: Novel Translation Pipeline
- หัวข้อ: V6.34 M3 baseline scan and glossary approval gate
- ผู้บันทึก: Codex
- สถานะ: เสร็จสิ้น
- Artifact หลัก:
  - `07_Reports/v6_34_m3_baseline_glossary_gate_decisions_20260701.md`
  - `Deep Sea Embers/04_Work/_experiments/v6_34_m3_dse_baseline_v1/`
  - `Horror Game Developers/04_Work/_experiments/v6_34_m3_hgd_baseline_v1/`
  - `Infinite Regressor Stories/04_Work/_experiments/v6_34_m3_irs_baseline_v1/`

## 2. วัตถุประสงค์

รอบนี้มีเป้าหมายเพื่อเริ่ม Milestone 3 ของ V6.34 โดยสร้าง experiment vault แยกสำหรับ DSE, HGD, และ IRS จาก sample manifest ที่ lock ใน Milestone 2 จากนั้นรัน scan-only gate และ commit glossary approval gate ให้พร้อมสำหรับ baseline translation

หลักสำคัญของรอบนี้คือ baseline ต้องไม่ถูก tune ก่อนวัดผล จึงตั้งนโยบายว่า candidate ใหม่ทั้งหมดจาก scan จะถูก hold out ใน baseline รอบนี้ และให้ pipeline ใช้ glossary เดิมที่ copy เข้า experiment vault เท่านั้น

## 3. วิธีการและขั้นตอน

1. สร้าง isolated experiment vaults:
   - `Deep Sea Embers/04_Work/_experiments/v6_34_m3_dse_baseline_v1`
   - `Horror Game Developers/04_Work/_experiments/v6_34_m3_hgd_baseline_v1`
   - `Infinite Regressor Stories/04_Work/_experiments/v6_34_m3_irs_baseline_v1`
2. Copy runtime/config/glossary/profile/prompts/scripts และเฉพาะ raw source in-sample 10 ตอนต่อเรื่องเข้า vault
3. Patch เฉพาะ `.system/providers.yaml` ในแต่ละ experiment vault เพื่อให้ Codex fallback `--cd` ชี้ experiment vault ไม่ใช่ production root
4. รัน preflight ในแต่ละ vault
5. รัน scan-only gate:

```powershell
novel-pipeline --config ".system/config.yaml" run --range "<in-sample chapters>" --run-id <run-id> --stop-after glossary-scan
```

6. สร้าง decision report:

```powershell
07_Reports/v6_34_m3_baseline_glossary_gate_decisions_20260701.md
```

7. Commit batch glossary gate:

```powershell
novel-pipeline --config ".system/config.yaml" approve-terms --batch --run-id <run-id> --decision-report "07_Reports/v6_34_m3_baseline_glossary_gate_decisions_20260701.md"
```

## 4. ผลการศึกษาและข้อมูลดิบ

### Vault และ preflight

| Novel | Vault | Preflight |
|---|---|---|
| DSE | `Deep Sea Embers/04_Work/_experiments/v6_34_m3_dse_baseline_v1` | ready |
| HGD | `Horror Game Developers/04_Work/_experiments/v6_34_m3_hgd_baseline_v1` | ready |
| IRS | `Infinite Regressor Stories/04_Work/_experiments/v6_34_m3_irs_baseline_v1` | ready |

### Scan results

| Novel | Run ID | Candidate Count | `fetched` | `glossary_scanned` | `glossary_approved` | Translation Records |
|---|---|---:|---:|---:|---:|---:|
| DSE | `v6-34-m3-dse-baseline-v1` | 32 | 10 | 10 | 10 | 0 |
| HGD | `v6-34-m3-hgd-baseline-v1` | 25 | 10 | 10 | 10 | 0 |
| IRS | `v6-34-m3-irs-baseline-v1` | 122 | 10 | 10 | 10 | 0 |

### Baseline glossary decision

| Decision | Reason |
|---|---|
| Hold all new candidates | Avoid tuning the pipeline before baseline measurement |
| Commit `glossary_approved` | Allow baseline translation to proceed with existing copied glossary |
| No new glossary notes | Prevent baseline contamination |
| No production glossary mutation | Experiment vault only |

## 5. ปัญหา อุปสรรค และการแก้ไข

### ปัญหา 1: provider config มี `--cd` เป็น absolute production root

- สิ่งที่เกิดขึ้น: ถ้า copy `.system/providers.yaml` ตรง ๆ ไปยัง experiment vault, Codex fallback จะชี้ production root
- วิธีแก้: patch เฉพาะ provider config copy ใน experiment vault ให้ `--cd` ชี้ vault ของแต่ละเรื่อง
- ผลลัพธ์หลังแก้: preflight ของทั้งสาม vault เป็น `ready`

### ปัญหา 2: candidate list มี noise จำนวนมาก

- สิ่งที่เกิดขึ้น: HGD และ IRS มี candidate ที่เป็น fragment/noise เช่น `Both Kyle`, `Did Kyle`, `Any NASA` และ title fragments
- วิธีแก้: baseline round hold all new candidates และบันทึกเป็น decision report แทนการ approve แบบเดาสุ่ม
- ผลลัพธ์หลังแก้: baseline จะวัดผลจาก current glossary state โดยไม่ tune ก่อนเวลา

## 6. ข้อสรุปและก้าวต่อไป

ข้อสรุป: M3 scan/glossary gate พร้อมสำหรับ baseline translation แล้ว ทั้งสาม experiment vault มี `fetched`, `glossary_scanned`, และ `glossary_approved` ครบ 10/10 chapters โดยยังไม่มี translation records

- DSE candidate count: 32
- HGD candidate count: 25
- IRS candidate count: 122
- Production output, production glossary, และ MoonRead ไม่ถูกแตะ

ก้าวต่อไป:

1. รัน baseline translation/refinement/QA/format/Sentinel ทีละ novel เริ่มจาก DSE หรือ HGD ตามความเสี่ยงที่ต้องการวัด
2. ห้ามแก้ systemic pipeline ระหว่าง baseline round
3. ถ้าเจอ provider failure, manual QA prompt, validation failure, หรือ Sentinel blocker/major ให้หยุดและบันทึกเป็น baseline failure data
