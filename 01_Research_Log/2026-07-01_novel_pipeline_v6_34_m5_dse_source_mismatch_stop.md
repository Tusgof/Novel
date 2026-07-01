# บันทึกการวิจัย: V6.34 M5 DSE Treatment Source Mismatch Stop

## 1. ข้อมูลพื้นฐาน

- Timestamp UTC: `2026-07-01T01:10:25Z`
- โครงการ: Novel Translation Pipeline
- หัวข้อ: DSE treatment หยุดเพราะ experiment raw source ไม่ตรง production raw
- ผู้บันทึก: Codex
- สถานะ: ยกเลิก
- Artifact หลัก:
  - `07_Reports/v6_34_m5_dse_treatment_source_mismatch_stop_20260701.md`
  - `scripts/verify_experiment_source_parity.py`
  - `Deep Sea Embers/04_Work/_experiments/v6_34_m5_dse_treatment_v1_invalid_source_mismatch_20260701`

## 2. วัตถุประสงค์

รอบนี้ตั้งใจเริ่ม DSE treatment measurement ตาม V6.34 M5 หลัง HGD comparison ผ่านจุดตัดสินใจแล้ว เป้าหมายคือวัดว่า treatment set ที่ช่วย HGD จะทำงานกับ DSE ได้หรือไม่ใน isolated experiment vault

ความสำเร็จของรอบนี้ควรเป็น DSE treatment output ที่เกิดจาก raw source ถูกต้องและวัดผลด้วย Sentinel ได้ แต่รอบนี้ต้องหยุดก่อน เพราะพบว่า experiment raw source ไม่ตรง production raw source ปัจจุบัน

## 3. วิธีการและขั้นตอน

1. สร้าง experiment vault `v6_34_m5_dse_treatment_v1` จาก DSE M3 baseline vault
2. เปลี่ยน ledger run id เป็น `v6-34-m5-dse-treatment-v1`
3. แก้ batch artifact ให้ใช้ run id treatment
4. รัน bounded resume เฉพาะ `ch017`:

```powershell
novel-pipeline --config ".system/config.yaml" resume --run-id v6-34-m5-dse-treatment-v1 --until-chapter ch017 --manual-action-mode stop
```

5. เมื่อ final assembly หยุดเพราะ title glossary violation จึงตรวจ `title.json`, experiment `source.json`, production `source.json`, และ glossary notes
6. เพิ่ม read-only parity checker:

```powershell
python scripts/verify_experiment_source_parity.py --novel-root "Deep Sea Embers" --experiment-root "Deep Sea Embers/04_Work/_experiments/v6_34_m5_dse_treatment_v1" --chapters "ch017,ch034,ch048,ch060,ch081,ch094,ch114,ch142,ch161,ch168"
```

## 4. ผลการศึกษาและข้อมูลดิบ

### ผลที่พบ

| Metric | Result |
|---|---:|
| DSE sampled chapters checked | 10 |
| Source parity mismatches | 10 |
| Valid treatment outputs produced | 0 |
| Production outputs changed | 0 |
| MoonRead changed | 0 |

### ตัวอย่าง mismatch

| Chapter | Experiment title | Production title |
|---|---|---|
| `ch017` | `第十六章 灵界行走` | `第十七章 洞穴` |
| `ch034` | `第三十三章 鱼` | `第三十四章 丰收` |
| `ch048` | `第四十七章 在圣像前` | `第四十八章 警觉` |

### การตีความ

ข้อมูลนี้ชี้ว่า experiment vault ที่ copy มาจาก baseline ไม่สามารถใช้วัด treatment ได้ เพราะ raw source ภายใน vault ไม่ตรงกับ source-of-truth ปัจจุบันของนิยาย

## 5. ปัญหา อุปสรรค และการแก้ไข

1. ปัญหา: `ch017` final assembly หยุดด้วย title glossary violation
   - วิธีแก้: ตรวจ source/title แทนการ patch ชื่อตอนเฉพาะหน้า
   - ผลลัพธ์: พบสาเหตุจริงคือ experiment raw stale/off-by-one

2. ปัญหา: ไม่มี gate ที่บังคับเทียบ experiment raw กับ production raw ก่อน provider calls
   - วิธีแก้: เพิ่ม `scripts/verify_experiment_source_parity.py`
   - ผลลัพธ์: สามารถตรวจ mismatch ได้แบบ deterministic ก่อนเริ่ม treatment/OOS รอบถัดไป

3. ข้อจำกัดสำคัญ: `ch017` artifacts ที่แปลไปแล้วต้องถือเป็น invalid experiment data เพราะแปลจาก raw ที่ผิด

## 6. ข้อสรุปและก้าวต่อไป

ข้อสรุป: DSE treatment รอบนี้ต้องยกเลิกและสร้าง experiment vault ใหม่ เพราะ raw source ใน vault ผิดทั้ง 10 sampled chapters

- ปัญหานี้เป็น Layer 0 experiment isolation/source-parity gate ไม่ใช่ปัญหา provider หรือคุณภาพการแปล
- Sentinel/title guard ทำหน้าที่ได้ดีพอที่จะหยุดก่อนสร้าง final output
- ต้องเพิ่ม source-parity check เป็นขั้นบังคับก่อน treatment/OOS resume ทุกครั้ง

ก้าวต่อไป:
1. สร้าง DSE treatment vault ใหม่จาก production raw ปัจจุบัน
2. รัน `scripts/verify_experiment_source_parity.py` ให้ mismatch เป็น 0 ก่อน provider calls
3. Restart DSE treatment measurement จาก `ch017`
