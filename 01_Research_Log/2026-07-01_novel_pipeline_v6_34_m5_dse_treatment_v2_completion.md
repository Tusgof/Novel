# บันทึกการวิจัย: V6.34 M5 DSE Treatment V2 Completion

## 1. ข้อมูลพื้นฐาน

- Timestamp UTC: `2026-07-01T03:46:19Z`
- โครงการ: Novel Translation Pipeline
- หัวข้อ: V6.34 Milestone 5 Deep Sea Embers treatment rerun after source-parity rebuild
- ผู้บันทึก: Codex
- สถานะ: เสร็จสิ้น
- Artifact หลัก:
  - `07_Reports/v6_34_m5_dse_treatment_v2_completion_20260701.md`
  - `Deep Sea Embers/04_Work/_experiments/v6_34_m5_dse_treatment_v2/`
  - `scripts/verify_experiment_source_parity.py`

## 2. วัตถุประสงค์

รอบนี้ต้องตอบคำถามว่า DSE treatment slice จะให้ผลวัดที่เชื่อถือได้หรือไม่ หลังจาก attempt ก่อนหน้าถูกยกเลิกเพราะ experiment vault มี raw source stale/off-by-one ทั้ง 10 sampled chapters

ความสำเร็จในรอบนี้คือ:

- experiment raw source ต้องตรงกับ production raw source สำหรับ sampled chapters ทั้งหมด
- treatment run ต้องจบครบ 10 sampled chapters โดยไม่มี current failed blocks
- latest scoped Sentinel ต้องเป็น `0/0/0/0` ทุก chapter
- ผลลัพธ์ต้องอยู่ใน experiment vault เท่านั้น ไม่แตะ production output หรือ MoonRead

## 3. วิธีการและขั้นตอน

1. สร้าง experiment vault ใหม่ `v6_34_m5_dse_treatment_v2` จาก current production raw/title sidecars และ production `03_Raw/manifest.json`
2. ตรวจ source parity ก่อน provider call:

```powershell
python scripts/verify_experiment_source_parity.py --novel-root "Deep Sea Embers" --experiment-root "Deep Sea Embers/04_Work/_experiments/v6_34_m5_dse_treatment_v2" --chapters "ch017,ch034,ch048,ch060,ch081,ch094,ch114,ch142,ch161,ch168"
```

3. รัน scan-only gate แล้ว approve experiment-local glossary records โดยไม่สร้าง production glossary notes ใหม่
4. รัน bounded resume ทีละ chapter และหยุดตรวจหลังแต่ละช่วง:

```powershell
novel-pipeline --config ".system/config.yaml" resume --run-id v6-34-m5-dse-treatment-v2 --until-chapter ch017 --manual-action-mode stop
novel-pipeline --config ".system/config.yaml" resume --run-id v6-34-m5-dse-treatment-v2 --until-chapter ch034 --manual-action-mode stop
novel-pipeline --config ".system/config.yaml" resume --run-id v6-34-m5-dse-treatment-v2 --until-chapter ch048 --manual-action-mode stop
novel-pipeline --config ".system/config.yaml" resume --run-id v6-34-m5-dse-treatment-v2 --until-chapter ch060 --manual-action-mode stop
novel-pipeline --config ".system/config.yaml" resume --run-id v6-34-m5-dse-treatment-v2 --until-chapter ch081 --manual-action-mode stop
novel-pipeline --config ".system/config.yaml" resume --run-id v6-34-m5-dse-treatment-v2 --until-chapter ch094 --manual-action-mode stop
novel-pipeline --config ".system/config.yaml" resume --run-id v6-34-m5-dse-treatment-v2 --until-chapter ch114 --manual-action-mode stop
novel-pipeline --config ".system/config.yaml" resume --run-id v6-34-m5-dse-treatment-v2 --until-chapter ch142 --manual-action-mode stop
novel-pipeline --config ".system/config.yaml" resume --run-id v6-34-m5-dse-treatment-v2 --until-chapter ch161 --manual-action-mode stop
novel-pipeline --config ".system/config.yaml" resume --run-id v6-34-m5-dse-treatment-v2 --until-chapter ch168 --manual-action-mode stop
```

5. ตรวจ final status, source parity, and latest scoped Sentinel reports

## 4. ผลการศึกษาและข้อมูลดิบ

### ผลที่ดี

| Metric | Result |
|---|---:|
| Sample chapters | 10 |
| Completed blocks | 56/56 |
| Current failed blocks | 0 |
| Manual actions needed | 0 |
| Source parity mismatches | 0 |
| Latest Sentinel blocker/major/minor/info | 0/0/0/0 for every sampled chapter |
| Production output/MoonRead changes | 0 |

### Stage counts

| Stage | Completed | Failed |
|---|---:|---:|
| fetched | 10 | 0 |
| glossary_scanned | 10 | 0 |
| glossary_approved | 10 | 0 |
| translating | 56 | 0 |
| refining | 62 | 1 |
| qa | 56 | 0 |
| formatting | 56 | 0 |
| completed | 56 | 0 |
| sentinel | 55 | 0 |

### Latest Sentinel evidence

| Chapter | Result |
|---|---|
| ch017 | 0/0/0/0 |
| ch034 | 0/0/0/0 |
| ch048 | 0/0/0/0 |
| ch060 | 0/0/0/0 |
| ch081 | 0/0/0/0 |
| ch094 | 0/0/0/0 |
| ch114 | 0/0/0/0 |
| ch142 | 0/0/0/0 |
| ch161 | 0/0/0/0 |
| ch168 | 0/0/0/0 |

### ผลที่ยังไม่ผ่านหรือยังพิสูจน์ไม่ได้

- ยังไม่ได้พิสูจน์ cross-novel generalization เพราะ IRS treatment measurement ยังไม่เสร็จ
- ยังพบ provider smoothness risk 1 ครั้ง: OpenRouter returned an empty assistant message ใน `ch094-block-005` refining แต่ระบบ retry/recovery จน latest state complete

## 5. ปัญหา อุปสรรค และการแก้ไข

1. ปัญหา: DSE treatment v1 ก่อนหน้าใช้ raw source stale/off-by-one จาก copied experiment vault และ stale manifest
   - การแก้ไข: quarantine invalid vaults, rebuild v2 จาก production raw/title sidecars และ production `03_Raw/manifest.json`, แล้วบังคับ source parity ก่อน provider call
   - ผลลัพธ์: final parity check เป็น `Checked 10 chapters`, `Mismatches: 0`

2. ปัญหา: OpenRouter refining หนึ่งครั้งคืน empty assistant message
   - การแก้ไข: pipeline retry/fallback ทำให้ latest state ของ `ch094-block-005` complete
   - ผลลัพธ์: status final ไม่มี current failed blocks แต่ยังบันทึกเป็น historical failed record 1 รายการ

## 6. ข้อสรุปและก้าวต่อไป

ข้อสรุป: DSE treatment v2 เป็น measurement round ที่ valid และ clean ภายใต้ gate ปัจจุบัน แต่ยังไม่พอสำหรับสรุป production mode เพราะ IRS treatment ยังไม่เสร็จ

- source-parity guard แก้ปัญหา experiment vault stale/off-by-one ได้จริงใน DSE
- treatment slice ผ่าน 10/10 sampled chapters และ latest Sentinel เป็น `0/0/0/0`
- provider smoothness ยังต้องนับเป็นความเสี่ยง ไม่ควรถูกตีความว่า long-run production พร้อมแล้ว

ก้าวต่อไป:
1. ทำ IRS treatment measurement ใน isolated experiment vault ให้ครบก่อนเริ่ม OOS Milestone 6
2. เปรียบเทียบ HGD + DSE + IRS treatment evidence ก่อนเลือกว่าจะไป OOS ด้วย treatment เดิมหรือแก้ hypothesis เพิ่ม
3. เก็บ source-parity guard เป็น required pre-provider gate สำหรับ experiment vaults ต่อไป
