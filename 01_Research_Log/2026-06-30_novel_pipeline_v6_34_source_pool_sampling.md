# บันทึกการวิจัย: V6.34 Source Pool และ Sample Manifest ข้ามนิยาย

## 1. ข้อมูลพื้นฐาน

- Timestamp UTC: `2026-06-30T22:15:47Z`
- โครงการ: Novel Translation Pipeline
- หัวข้อ: V6.34 source-pool audit and cross-novel sampling
- ผู้บันทึก: Codex
- สถานะ: เสร็จสิ้น
- Artifact หลัก:
  - `07_Reports/v6_34_m2_source_pool_and_sample_manifest_20260701.md`
  - `IMPLEMENT_PLAN.md`
  - `PROJECT_BRAIN.md`

## 2. วัตถุประสงค์

รอบนี้มีเป้าหมายเพื่อทำ Milestone 2 ของ V6.34: ตรวจว่า raw source pool ของนิยายทั้งสามเรื่องพร้อมสำหรับการสุ่มหรือไม่ และสร้าง sample manifest ที่ reproducible จาก raw source เท่านั้น

รอบนี้สำคัญเพราะผู้ใช้กำหนดชัดว่า Libra - Pilot ต้องสุ่มจาก source raw ไม่ใช่เฉพาะตอนที่เคยแปลหรือเคยมีปัญหา และถ้า fetch ยังไม่ครบต้อง fetch ให้ครบก่อนสุ่ม การทดลองจึงต้องเริ่มจากหลักฐานว่า source pool ปัจจุบันครบภายในขอบเขตที่ตรวจได้

## 3. วิธีการและขั้นตอน

1. ตรวจ `03_Raw/` ของนิยายทั้งสามเรื่อง:
   - `Deep Sea Embers/03_Raw`
   - `Horror Game Developers/03_Raw`
   - `Infinite Regressor Stories/03_Raw`
2. สำหรับแต่ละเรื่อง ตรวจ:
   - จำนวน chapter directory
   - เลข chapter ต่ำสุด/สูงสุด
   - gaps ระหว่าง min/max
   - `source.json` ที่หาย
   - `source.json` ที่อ่าน JSON ไม่ได้
3. ใช้ seed `634001` เพื่อสุ่มแบบ reproducible
4. แบ่งแต่ละนิยายเป็น 10 strata ตามเลข chapter
5. สุ่ม 2 ตอนต่อ stratum:
   - ตอนแรกเป็น `in_sample`
   - ตอนที่สองเป็น `out_of_sample`
6. บันทึกผลใน `07_Reports/v6_34_m2_source_pool_and_sample_manifest_20260701.md`

ไม่มีการเรียก provider ไม่มีการรัน translation pipeline และไม่มีการ publish MoonRead ในรอบนี้

## 4. ผลการศึกษาและข้อมูลดิบ

### Source pool audit

| Novel | Count | Min | Max | Gaps | Missing source | Unreadable source |
|---|---:|---:|---:|---:|---:|---:|
| DSE | 180 | 1 | 180 | 0 | 0 | 0 |
| HGD | 270 | 1 | 270 | 0 | 0 | 0 |
| IRS | 394 | 1 | 394 | 0 | 0 | 0 |

### Sample summary

| Novel | In-sample | Out-of-sample | Total |
|---|---:|---:|---:|
| DSE | 10 | 10 | 20 |
| HGD | 10 | 10 | 20 |
| IRS | 10 | 10 | 20 |
| Total | 30 | 30 | 60 |

### In-sample chapters

- DSE: `ch017`, `ch034`, `ch048`, `ch060`, `ch081`, `ch094`, `ch114`, `ch142`, `ch161`, `ch168`
- HGD: `ch024`, `ch037`, `ch066`, `ch103`, `ch132`, `ch142`, `ch170`, `ch196`, `ch225`, `ch250`
- IRS: `ch020`, `ch067`, `ch080`, `ch119`, `ch160`, `ch207`, `ch261`, `ch276`, `ch322`, `ch361`

### Out-of-sample chapters

- DSE: `ch009`, `ch029`, `ch047`, `ch070`, `ch088`, `ch095`, `ch124`, `ch143`, `ch148`, `ch174`
- HGD: `ch015`, `ch046`, `ch060`, `ch101`, `ch131`, `ch153`, `ch184`, `ch192`, `ch226`, `ch262`
- IRS: `ch012`, `ch053`, `ch095`, `ch144`, `ch187`, `ch208`, `ch258`, `ch290`, `ch323`, `ch372`

## 5. ปัญหา อุปสรรค และการแก้ไข

ไม่พบปัญหาในรอบนี้

ข้อจำกัดสำคัญ:

- ขอบเขต IRS ใช้ local verified raw scope ถึง `ch394` เพราะ source หลังจากนั้นเคยมีข้อจำกัดจาก upstream
- รอบนี้เป็น sampling/read-only gate เท่านั้น ยังไม่ได้วัดคุณภาพ translation

## 6. ข้อสรุปและก้าวต่อไป

ข้อสรุป: Milestone 2 ผ่านเงื่อนไข source-pool/sampling gate แล้ว เพราะทั้งสามเรื่องมี raw source ครบภายในขอบเขตที่ตรวจได้ และ sample manifest ถูกสร้างจาก raw source ด้วย seed คงที่

- DSE, HGD, IRS ไม่มี gaps ใน raw source pool ปัจจุบัน
- ไม่ต้อง fetch เพิ่มก่อนเริ่ม baseline รอบนี้
- Sample ครอบคลุมทั้งสามเรื่องเท่ากัน
- Experiment output ยังคงถูกแยกจาก production output และ MoonRead

ก้าวต่อไป:

1. เริ่ม Milestone 3 baseline round จาก in-sample 30 ตอน
2. เริ่มด้วย scan-only และ glossary gate ใน isolated experiment state
3. ห้ามแก้ systemic pipeline ระหว่าง baseline จนกว่าจะจบรอบและวิเคราะห์ defect
