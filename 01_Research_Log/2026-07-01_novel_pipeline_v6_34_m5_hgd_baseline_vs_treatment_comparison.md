# บันทึกการวิจัย: V6.34 M5 HGD Baseline vs Treatment Comparison

## 1. ข้อมูลพื้นฐาน

- Timestamp UTC: `2026-07-01T00:54:57Z`
- โครงการ: Novel Translation Pipeline
- หัวข้อ: เปรียบเทียบ HGD baseline กับ treatment ใน V6.34 M5
- ผู้บันทึก: Codex
- สถานะ: เสร็จสิ้น
- Artifact หลัก:
  - `07_Reports/v6_34_m5_hgd_baseline_vs_treatment_comparison_20260701.md`
  - `Horror Game Developers/04_Work/_experiments/v6_34_m3_hgd_baseline_v1/06_Logs/run_ledger.jsonl`
  - `Horror Game Developers/04_Work/_experiments/v6_34_m5_hgd_treatment_v1/06_Logs/run_ledger.jsonl`

## 2. วัตถุประสงค์

รอบนี้ตอบคำถามว่า treatment ที่เพิ่มหลัง baseline stop ของ HGD ทำให้ผลวัดดีขึ้นจริงหรือไม่ โดยเน้นผลลัพธ์ที่ตรวจได้จาก ledger, Sentinel, และรายงาน experiment ไม่ใช่การประเมินด้วยความรู้สึก

ความสำเร็จของรอบนี้คือมีหลักฐานชัดเจนว่า treatment ลด defect ที่ baseline เจอได้หรือไม่ และตัดสินใจได้ว่าควรไปต่อกับ DSE/IRS treatment measurement หรือควรแก้ treatment ก่อน

## 3. วิธีการและขั้นตอน

1. ตรวจสถานะ baseline HGD:

```powershell
novel-pipeline --config ".system/config.yaml" status --run-id v6-34-m3-hgd-baseline-v1
```

2. ตรวจสถานะ treatment HGD:

```powershell
novel-pipeline --config ".system/config.yaml" status --run-id v6-34-m5-hgd-treatment-v1
```

3. อ่าน Sentinel baseline ที่หยุดบน `ch037` และ treatment completion report
4. นับ ledger records แยกตาม stage/provider/status
5. เขียน comparison report และสรุป decision สำหรับขั้นถัดไป

## 4. ผลการศึกษาและข้อมูลดิบ

### สรุปตัวเลขเปรียบเทียบ

| Metric | Baseline | Treatment | การเปลี่ยนแปลง |
|---|---:|---:|---|
| Planned HGD in-sample chapters | 10 | 10 | คงเดิม |
| Completed chapters ก่อน stop/final status | 2 | 10 | ดีขึ้น |
| Current failed blocks/chapters | 1 | 0 | ดีขึ้น |
| `ch037` latest Sentinel | `0/2/0/0` | `0/0/0/0` | ดีขึ้น |
| Treatment latest Sentinel ทั้ง 10 ตอน | ไม่ครบ เพราะ baseline หยุดก่อน | `0/0/0/0` ทุกตอน | ดีขึ้น |
| Historical failed records | 1 | 6 | ยังเป็นความเสี่ยงด้าน smoothness |
| QA hard-fail records | 0 | 2 | ยังเป็นความเสี่ยงด้าน smoothness |
| QA omission literal-safe recovery | ไม่พบก่อน baseline stop | 5 ตอน | ยังเป็นความเสี่ยงด้าน omission |

### ผลที่ดี

- Treatment แก้ baseline defect ที่ `ch037` ได้จริง: `Velora Art Museum` / `Art Museum` ถูกบังคับให้ตรงกับ `พิพิธภัณฑ์ศิลปะเวโลรา`
- Treatment run จบ HGD in-sample ครบ 10/10 ตอน
- Latest scoped Sentinel ของ treatment ทั้ง 10 ตอนเป็น `0/0/0/0`
- Experiment output ไม่ถูก publish ไป MoonRead และไม่ปน production output

### ผลที่ยังไม่ผ่านหรือยังต้องระวัง

- Treatment ยังต้องใช้ recovery หลายครั้ง โดยเฉพาะ QA omission literal-safe recovery 5 ตอน
- มี QA hard-fail 2 records ใน treatment (`ch132`, `ch250`)
- ความสำเร็จตอนนี้ยังพิสูจน์เฉพาะ HGD treatment slice ยังไม่ใช่หลักฐาน cross-novel ครบทั้ง DSE/HGD/IRS

## 5. ปัญหา อุปสรรค และการแก้ไข

1. ปัญหา: baseline หยุดเร็วหลัง `ch037` ทำให้ไม่มี baseline เต็ม 10 ตอนสำหรับ HGD
   - วิธีจัดการ: ใช้ baseline stop เป็น valid gate ตามแผน เพราะ defect เป็น true positive ที่ต้องหยุด ไม่ใช่ provider outage
   - ผลลัพธ์: สามารถเปรียบเทียบจุดหยุดเดิม (`ch037`) กับ treatment ได้ตรงจุด และใช้ treatment completion เป็นหลักฐานต่อ

2. ปัญหา: treatment ผ่าน output surface แต่ยังมี recovery สูง
   - วิธีจัดการ: บันทึกเป็น operational caveat ไม่สรุปเกินหลักฐาน
   - ผลลัพธ์: decision คือไปต่อ DSE/IRS treatment measurement แบบ isolated ก่อน ไม่เลื่อนไป production scaling

## 6. ข้อสรุปและก้าวต่อไป

ข้อสรุป: HGD treatment ดีขึ้นจริงในมิติ Sentinel/product-surface แต่ยังไม่พอจะสรุปว่า pipeline พร้อมรันยาวแบบ production โดยไม่ต้องคุม

- หลักฐานด้านคุณภาพ output ดีขึ้น: `ch037` จาก `0/2/0/0` เป็น `0/0/0/0` และ treatment ทั้ง 10 ตอนเป็น `0/0/0/0`
- หลักฐานด้าน long-run smoothness ยังไม่พอ: มี hard-fail/recovery ระหว่างทางหลายจุด
- การตีความ: treatment set ควรไปต่อใน DSE/IRS เพื่อดูว่า defect เป็น cross-novel หรือ HGD-specific ก่อนตัดสินใจ production mode

ก้าวต่อไป:
1. รัน DSE treatment measurement ใน isolated experiment vault
2. รัน IRS treatment measurement ใน isolated experiment vault
3. เปรียบเทียบ DSE/HGD/IRS treatment metrics รวมก่อนเข้าสู่ out-of-sample M6
4. ห้าม publish experiment output ไป MoonRead จนกว่าจะมี production gate แยก

