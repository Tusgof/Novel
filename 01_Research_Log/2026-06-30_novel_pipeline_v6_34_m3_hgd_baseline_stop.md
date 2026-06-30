# บันทึกการวิจัย: V6.34 M3 Baseline หยุดที่ HGD ch037

## 1. ข้อมูลพื้นฐาน

- Timestamp UTC: `2026-06-30T22:47:02Z`
- โครงการ: Novel Translation Pipeline
- หัวข้อ: V6.34 M3 HGD baseline translation stop
- ผู้บันทึก: Codex
- สถานะ: เสร็จสิ้นแบบหยุดตาม gate
- Artifact หลัก:
  - `Horror Game Developers/04_Work/_experiments/v6_34_m3_hgd_baseline_v1/`
  - `07_Reports/sentinel_quality_manual_experiment_ch037_probe_20260630_224633.md`
  - `07_Reports/sentinel_quality_v6-34-m3-hgd-baseline-v1_ch037_sentinel_20260630_224252.md`

## 2. วัตถุประสงค์

รอบนี้เป็น baseline translation attempt แรกของ Milestone 3 โดยเลือกเริ่มจาก HGD เพราะมี 10 blocks เท่านั้น เหมาะสำหรับพิสูจน์ว่า experiment vault และ baseline gate ทำงานได้ก่อนขยายไป DSE/IRS ที่มีจำนวน block มากกว่า

เป้าหมายคือรัน translation/refinement/QA/format/Sentinel โดยไม่แก้ systemic pipeline ระหว่างทาง หากเจอ Sentinel blocker/major ต้องหยุดและบันทึกเป็น baseline failure data

## 3. วิธีการและขั้นตอน

1. รัน baseline resume จาก HGD experiment vault:

```powershell
cd "D:\Fogust\Workspace\Novel\Horror Game Developers\04_Work\_experiments\v6_34_m3_hgd_baseline_v1"
$env:PYTHONIOENCODING='utf-8'
novel-pipeline --config ".system/config.yaml" resume --run-id v6-34-m3-hgd-baseline-v1 --manual-action-mode stop
```

2. รอบแรกหยุดที่ `ch024` เพราะ experiment vault ไม่มี title sidecar:
   - error: `Missing HGD Thai title mapping for ch024`
   - action: copy title sidecars ของ sampled chapters จาก production vault เข้า experiment vault
   - classification: experiment setup issue, not translation treatment

3. Resume ต่อหลัง copy title sidecars

4. รอบที่สองหยุดที่ `ch037` เพราะ Sentinel gate เจอ major findings

5. ตรวจพบว่า runtime Sentinel report แรกอ้าง production output/MoonRead เพราะ Sentinel ยังไม่ experiment-vault aware

6. ทำ instrumentation fix:
   - `Deep Sea Embers/scripts/sentinel_quality_report.py` รองรับ env override สำหรับ workspace/registry/report root
   - `Deep Sea Embers/novel_pipeline/pipeline.py` ตั้ง env override อัตโนมัติเมื่อ workspace อยู่ใต้ `_experiments` และมี local registry
   - เพิ่ม local `00_Config/novel_registry.json` ใน experiment vaults

7. รัน manual Sentinel probe ซ้ำบน HGD experiment vault เพื่อแยก production false reference ออก

## 4. ผลการศึกษาและข้อมูลดิบ

### Baseline progress

| Item | Result |
|---|---:|
| HGD sampled chapters | 10 |
| Chapters fully written before stop | 2 |
| Completed blocks | 2 |
| Current failed chapter | `ch037` |
| Translation records started | yes |
| Production output modified | no |
| MoonRead modified | no |

### Provider/stage status at stop

| Stage/Provider | Result |
|---|---|
| openrouter translating | completed: 2 |
| openrouter refining | completed: 4 |
| openrouter_reasoning QA | completed: 1 |
| qwen QA | completed: 1 |
| openrouter formatting | completed: 1 |
| local Sentinel | completed: 1, failed: 1 |

### Sentinel result after experiment-local probe

| Report | Blocker | Major | Minor | Info |
|---|---:|---:|---:|---:|
| `sentinel_quality_manual_experiment_ch037_probe_20260630_224633.md` | 0 | 2 | 0 | 0 |

Findings:

- `Velora Art Museum -> พิพิธภัณฑ์ศิลปะเวโลรา` missing in experiment `ch037` final output
- `Art Museum -> พิพิธภัณฑ์ศิลปะเวโลรา` missing in experiment `ch037` final output

## 5. ปัญหา อุปสรรค และการแก้ไข

### ปัญหา 1: title sidecars ไม่ถูก copy เข้า experiment vault

- สิ่งที่เกิดขึ้น: HGD `ch024` final assembly fail เพราะไม่มี title sidecar ใน experiment vault
- วิธีแก้: copy `04_Work/<chapter>/title.json` สำหรับ sampled chapters เข้า experiment vault
- ผลลัพธ์หลังแก้: `ch024` ผ่านและ resume ต่อได้

### ปัญหา 2: Sentinel runtime report อ้าง production output/MoonRead

- สิ่งที่เกิดขึ้น: Sentinel report แรกของ `ch037` อ้าง `Horror Game Developers/05_Output` และ `MoonRead/content/generated` แทน experiment vault
- วิธีแก้: เพิ่ม env override ใน Sentinel และ pipeline runtime gate สำหรับ experiment vault พร้อม local registry
- ผลลัพธ์หลังแก้: manual Sentinel probe อ้าง experiment vault และลด findings จาก 4 เป็น 2 เพราะไม่รวม MoonRead production duplicate

### ปัญหา 3: baseline เจอ glossary coverage major จริง

- สิ่งที่เกิดขึ้น: Experiment output `ch037` ไม่ใช้ approved Thai term ของ `Velora Art Museum`
- วิธีแก้ในรอบนี้: ไม่แก้ output เพราะเป็น baseline data
- ผลลัพธ์หลังแก้: ไม่มีการแก้คำแปล; issue ถูกส่งต่อให้ Milestone 4 analysis

## 6. ข้อสรุปและก้าวต่อไป

ข้อสรุป: Milestone 3 baseline translation หยุดตาม gate ที่ HGD `ch037` และให้ข้อมูลสำคัญสองชั้นคือ experiment Sentinel instrumentation gap กับ glossary coverage failure จริง

- ไม่ควรแก้ `ch037` ระหว่าง baseline เพราะจะทำให้ before/after ปนกัน
- Sentinel สำหรับ experiment ต้องใช้ local registry ของ vault เสมอ
- ปัญหา `Velora Art Museum` ควรถูกวิเคราะห์ใน Milestone 4 ว่าเป็น Layer 0/1/2 หรือ run-local

ก้าวต่อไป:

1. Commit/push instrumentation fix และ research log นี้
2. เริ่ม Milestone 4 defect analysis จากข้อมูล M3 ที่หยุดตรง `ch037`
3. ตัดสิน treatment hypothesis ก่อน rerun
