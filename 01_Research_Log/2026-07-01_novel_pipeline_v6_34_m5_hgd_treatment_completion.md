# บันทึกการวิจัย: V6.34 M5 HGD Treatment Completion

## 1. ข้อมูลพื้นฐาน

- Timestamp UTC: `2026-07-01T00:48:42Z`
- โครงการ: Novel Translation Pipeline
- หัวข้อ: V6.34 M5 HGD treatment completion
- ผู้บันทึก: Codex
- สถานะ: HGD treatment slice เสร็จสิ้น
- Artifact หลัก:
  - `07_Reports/v6_34_m5_hgd_treatment_completion_20260701.md`
  - `Horror Game Developers/04_Work/_experiments/v6_34_m5_hgd_treatment_v1/06_Logs/run_ledger.jsonl`
  - `Horror Game Developers/04_Work/_experiments/v6_34_m5_hgd_treatment_v1/05_Output/`

## 2. วัตถุประสงค์

รอบนี้ต้องการรัน HGD treatment slice ของ V6.34 M5 ให้ครบ 10 in-sample chapters หลังจาก treatment ก่อนหน้าผ่าน `ch132`

ความสำเร็จคือทุก chapter ต้อง complete, current failed blocks ต้องเป็น none, และ latest scoped Sentinel ของทุก chapter ต้องเป็น `0/0/0/0`

## 3. วิธีการและขั้นตอน

1. Continue bounded resume ทีละ chapter ใน experiment vault:

```powershell
cd "D:\Fogust\Workspace\Novel\Horror Game Developers\04_Work\_experiments\v6_34_m5_hgd_treatment_v1"
$env:PYTHONIOENCODING='utf-8'
novel-pipeline --config ".system/config.yaml" resume --run-id v6-34-m5-hgd-treatment-v1 --until-chapter ch142 --manual-action-mode stop
novel-pipeline --config ".system/config.yaml" resume --run-id v6-34-m5-hgd-treatment-v1 --until-chapter ch170 --manual-action-mode stop
novel-pipeline --config ".system/config.yaml" resume --run-id v6-34-m5-hgd-treatment-v1 --until-chapter ch196 --manual-action-mode stop
novel-pipeline --config ".system/config.yaml" resume --run-id v6-34-m5-hgd-treatment-v1 --until-chapter ch225 --manual-action-mode stop
novel-pipeline --config ".system/config.yaml" resume --run-id v6-34-m5-hgd-treatment-v1 --until-chapter ch250 --manual-action-mode stop
```

2. เมื่อ `ch250` หยุดที่ QA hard-fail เพราะ source `-ranked Gate` ถูกเติมเป็น `ระดับ S`, เพิ่ม deterministic redacted-rank repair แล้ว rerun:

```powershell
cd "D:\Fogust\Workspace\Novel\Deep Sea Embers"
$env:PYTHONIOENCODING='utf-8'
python -m compileall novel_pipeline
python test_translation.py

cd "D:\Fogust\Workspace\Novel\Horror Game Developers\04_Work\_experiments\v6_34_m5_hgd_treatment_v1"
novel-pipeline --config ".system/config.yaml" rerun-block --run-id v6-34-m5-hgd-treatment-v1 --block-id ch250-block-001 --from-stage translating
```

3. ตรวจสถานะและ latest Sentinel reports หลังจบ run

## 4. ผลการศึกษาและข้อมูลดิบ

| Metric | Result |
|---|---|
| Records | `169` |
| Completed blocks | `10/10` |
| Current failed blocks | `0` |
| Historical hard-fail records | `2` |
| Latest Sentinel all chapters | `0/0/0/0` |
| QA omission literal-safe recoveries | `5` blocks |
| Redacted rank repair | `ch250-block-001`, `เกตระดับ S` -> `เกตไม่ระบุแรงก์` |
| MoonRead publication | not performed |

Latest Sentinel results:

| Chapter | Result |
|---|---|
| `ch024` | `0/0/0/0` |
| `ch037` | `0/0/0/0` |
| `ch066` | `0/0/0/0` |
| `ch103` | `0/0/0/0` |
| `ch132` | `0/0/0/0` |
| `ch142` | `0/0/0/0` |
| `ch170` | `0/0/0/0` |
| `ch196` | `0/0/0/0` |
| `ch225` | `0/0/0/0` |
| `ch250` | `0/0/0/0` |

## 5. ปัญหา อุปสรรค และการแก้ไข

1. ปัญหา: หลาย chapter ยังต้องใช้ QA omission literal-safe recovery เพื่อคืนเสียง/ความคิดที่ refinement ทำหล่น
   - การแก้ไข: ใช้ recovery path ที่มีอยู่ ไม่ force-accept
   - ผลลัพธ์: `ch024`, `ch066`, `ch142`, `ch170`, และ `ch196` ผ่าน QA/Sentinel

2. ปัญหา: `ch250` เติม rank ที่ source ไม่ได้ระบุ
   - การแก้ไข: เพิ่ม redacted-rank repair แบบแคบ ทำงานเฉพาะ source ที่มี `-ranked Gate` และไม่มี `S-ranked/S-Ranked Gate` จริง
   - ผลลัพธ์: literal artifact บันทึก repair metadata และ output ใช้ `เกตไม่ระบุแรงก์`

3. ปัญหา: `ch225` QA primary ไม่จบและ fallback ไป `qwen`
   - การแก้ไข: fallback ทำงานตาม routing
   - ผลลัพธ์: `ch225` complete และ Sentinel `0/0/0/0`

ข้อจำกัดสำคัญ: นี่เป็น HGD treatment slice เท่านั้น ยังไม่ใช่ M5 cross-novel completion สำหรับ DSE/IRS

## 6. ข้อสรุปและก้าวต่อไป

ข้อสรุป: HGD treatment slice ผ่านครบ 10/10 chapters และ latest Sentinel เป็น `0/0/0/0` ทุก chapter แต่ยังเผยให้เห็นว่า refinement omission ยังเกิดบ่อยและต้องวัดต่อเป็น metric หลัก

- Treatment แก้ defect เดิมของ baseline ได้จริงสำหรับ HGD
- Sentinel และ QA recovery ป้องกันไม่ให้ defect หลุดเป็น final experiment output
- Redacted-rank repair เป็นตัวอย่าง defect ที่ควรจัดเป็น Layer 0/ภาษาอังกฤษ source marker มากกว่าปัญหาเฉพาะ output เดียว

ก้าวต่อไป:
1. ทำ baseline-versus-treatment comparison ของ HGD slice
2. ตัดสินใจว่าจะรัน treatment ต่อกับ DSE/IRS in-sample หรือปรับ treatment ก่อน
3. ห้าม publish experiment output ไป MoonRead
