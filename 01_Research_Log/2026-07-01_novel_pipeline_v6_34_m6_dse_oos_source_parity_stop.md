# บันทึกการวิจัย: V6.34 M6 DSE OOS หยุดเพราะ source parity ผิด

## 1. ข้อมูลพื้นฐาน

- Timestamp UTC: `2026-07-01T09:57:43Z`
- โครงการ: Novel Translation Pipeline
- หัวข้อ: V6.34 Milestone 6 DSE out-of-sample source parity stop
- ผู้บันทึก: Codex
- สถานะ: ยกเลิก
- Artifact หลัก:
  - `07_Reports/v6_34_m6_dse_oos_source_parity_stop_20260701.md`
  - `Deep Sea Embers/04_Work/_experiments/v6_34_m6_dse_oos_v1/06_Logs/run_ledger.jsonl`
  - `scripts/verify_experiment_source_parity.py`

## 2. วัตถุประสงค์

รอบนี้ต้องตรวจว่าการรัน DSE out-of-sample ใน V6.34 Milestone 6 สามารถดำเนินต่อจาก HGD OOS ได้หรือไม่ โดยยังคงกฎ experiment-only และไม่แตะ production/MoonRead

ความสำเร็จคือ DSE OOS ต้องแปลครบ locked OOS chapters ด้วย source ที่ตรงกับ production raw ปัจจุบัน, ไม่มี current failed blocks, และไม่มี Sentinel blocker/major ก่อนจะนำไปเทียบกับ HGD/IRS

## 3. วิธีการและขั้นตอน

1. ตรวจ status ของ run `v6-34-m6-dse-oos-v1` หลังคำสั่ง resume รอบก่อน timeout
2. พบว่า run ยังเดินและ completed blocks เพิ่มจาก 8 เป็น 28 จึง monitor ต่อโดยไม่ kill process
3. เมื่อ run หยุดหลัง `ch088` ตรวจ status:

```powershell
novel-pipeline --config ".system/config.yaml" status --run-id v6-34-m6-dse-oos-v1
```

4. พบว่า `ch088` ทุก block complete แต่ `05_Output/ch088/ch088.md` missing จึงลอง rerun final assembly ผ่าน format stage:

```powershell
novel-pipeline --config ".system/config.yaml" rerun-block --run-id v6-34-m6-dse-oos-v1 --block-id ch088-block-006 --from-stage formatting
```

5. คำสั่งหยุดเพราะ title glossary validation
6. ตรวจ raw source/title sidecar ของ OOS chapters และรัน source parity checker จาก repo root:

```powershell
python scripts\verify_experiment_source_parity.py --novel-root "Deep Sea Embers" --experiment-root "Deep Sea Embers\04_Work\_experiments\v6_34_m6_dse_oos_v1" --chapters "ch009,ch029,ch047,ch070,ch088,ch095,ch124,ch143,ch148,ch174"
```

## 4. ผลการศึกษาและข้อมูลดิบ

### Run state

| Metric | Value |
|---|---:|
| Ledger records | 182 |
| Completed blocks | 28 |
| Current failed blocks | 0 |
| Historical failed records | 0 |
| Completed sampled chapters | `ch009`, `ch029`, `ch047`, `ch070` |
| Partially invalid completed chapter | `ch088` blocks complete but chapter output missing |

### Source parity

| Chapter | Production raw title | Experiment raw title | Finding |
|---|---|---|---|
| `ch009` | `第九章 去而复归又复归` | `第八章 太阳` | mismatch |
| `ch029` | `第二十九章 保护城市的人` | `第二十八章 苍白夜色` | mismatch |
| `ch047` | `第四十七章 在圣像前` | `第四十六章 异常与异象` | mismatch |
| `ch070` | `第七十章 自己人` | `第六十九章 城邦生活` | mismatch |
| `ch088` | `第八十八章 有一件真货` | `第八十七章 凡娜的调查结论` | mismatch |
| `ch095` | `第九十五章 渗透` | `第九十四章 妮娜的怪梦` | mismatch |
| `ch124` | `第125章 碎片的倒影` | `第124章 封存于记忆中` | mismatch |
| `ch143` | `第144章 催眠` | `第143章 问询与治疗` | mismatch |
| `ch148` | `第149章 迭加` | `第148章 出现在现实世界？` | mismatch |
| `ch174` | `第175章 风暴前夕` | `第174章 火在蔓延` | mismatch |

ผล checker:

```text
Checked 10 chapters
Mismatches: 10
```

## 5. ปัญหา อุปสรรค และการแก้ไข

1. **อาการ:** DSE OOS แปลผ่านหลาย block แต่ final assembly ของ `ch088` หยุดเพราะ title ไม่ตรง approved glossary `凡娜 -> ฟานน่า`
   - **การแก้ไข:** ตรวจ raw/title และพบว่า experiment raw source stale/off-by-one
   - **ผลลัพธ์:** หยุด DSE OOS ทันที ไม่ resume ต่อ

2. **อาการ:** เอกสารก่อนหน้าระบุว่า DSE OOS source parity เป็น `0` mismatches แต่ vault ปัจจุบัน mismatch `10/10`
   - **การแก้ไข:** รัน `scripts/verify_experiment_source_parity.py` จาก repo root ด้วย `--novel-root "Deep Sea Embers"` และ `--experiment-root` ที่ถูกต้อง
   - **ผลลัพธ์:** ยืนยันว่า checker จับปัญหาได้ แต่ workflow ก่อน provider calls ไม่ได้ enforce ผลตรวจจริง

ข้อจำกัดสำคัญ:

- Output ที่เกิดใน DSE OOS vault นี้ถือเป็น invalid measurement data เพราะ source ไม่ตรง production raw ปัจจุบัน
- ยังไม่ได้ rebuild vault ในรอบนี้ เพราะต้องหยุดเพื่อบันทึก evidence และป้องกันการวัดผลผิด

## 6. ข้อสรุปและก้าวต่อไป

ข้อสรุป: DSE OOS รอบ `v6-34-m6-dse-oos-v1` ต้องยกเลิก เพราะ experiment vault ใช้ raw source stale/off-by-one ทั้ง 10 sampled chapters

- ปัญหาไม่ได้อยู่ที่ provider แปลผิดเป็นหลัก แต่เป็น experiment source setup ผิด
- Final assembly title glossary gate ทำหน้าที่ถูกต้อง เพราะเป็นจุดแรกที่จับว่า source/title sidecar ไม่สัมพันธ์กัน
- Source parity checker ใช้งานได้ แต่ต้อง enforce ก่อน provider calls ทุกครั้ง ไม่ใช่แค่บันทึกในเอกสาร

ก้าวต่อไป:

1. Rebuild DSE OOS vault ใหม่จาก production `03_Raw/` และ `04_Work/<chapter>/title.json`
2. รัน `scripts/verify_experiment_source_parity.py` ให้ mismatch เป็น `0` ก่อน provider calls
3. Restart DSE OOS จากต้น sample ใน vault ใหม่ และทิ้ง partial measurement ของ `v6_34_m6_dse_oos_v1`
4. อัปเดต `PROJECT_BRAIN.md` และ `IMPLEMENT_PLAN.md` ให้ Next Safe Action ชัดเจนว่า DSE OOS ต้อง rebuild ก่อนเดินต่อ
