# Novel Operator Guide

คู่มือสั่งงานระบบแปลนิยายให้ได้มาตรฐานและมีประสิทธิภาพ

Last updated: 2026-07-02

## หลักสั้นที่สุด

เวลาจะสั่งงาน ให้บอก 4 อย่างนี้ก่อนเสมอ:

1. **เรื่องอะไร**  
   เช่น Deep Sea Embers, Horror Game Developer, Infinite Regressor Stories หรือนิยายเรื่องใหม่

2. **ต้องการทำอะไร**  
   แปลต่อ / ซ่อมตอน / setup เรื่องใหม่ / publish MoonRead / ตรวจคุณภาพ

3. **ช่วงไหน**  
   เช่น `ch211-ch215`, ตอน 164, ตอน 1-50

4. **ผลลัพธ์ที่ต้องการ**  
   เช่น แปลเสร็จแล้วอัป MoonRead, ซ่อมเฉพาะคำผิด, ตรวจสาเหตุและป้องกันไม่ให้เกิดซ้ำ

## 1. สั่งแปลนิยายต่อ

ใช้คำสั่งประมาณนี้:

```text
ช่วยแปล [ชื่อเรื่อง] ตอน [ช่วงตอน] ให้หน่อย
ใช้ workflow มาตรฐาน:
- scan glossary ก่อน
- approve/reject glossary อย่างระวัง
- แปลเป็น bounded batch
- รัน output guardrails + Sentinel
- spot-check หลังจบ batch
- publish ขึ้น MoonRead
- commit/push git
- ถ้าเจอ QA hard-fail/provider failure/manual prompt ให้หยุดและรายงานก่อน
```

ตัวอย่าง:

```text
ช่วยแปล Deep Sea Embers ch211-ch215 ให้หน่อย
ทำตาม workflow มาตรฐาน แปลเสร็จแล้วอัป MoonRead และ push git
```

ระบบควรทำ:

- รัน scan-only gate
- ตรวจ candidate glossary
- อนุมัติ glossary ที่ควรล็อกจริง
- แปลแบบ bounded batch
- หยุดถ้าเจอปัญหา
- ตรวจ output
- รัน Sentinel
- spot-check
- publish MoonRead
- commit/push

ขนาด batch ที่แนะนำตอนนี้คือ **5 ตอนต่อ batch** เช่น `ch211-ch215`, `ch216-ch220`

อย่าสั่งแปลยาวเกินไปในครั้งเดียว เพราะเพิ่มความเสี่ยงเรื่อง provider timeout, QA hard-fail, glossary drift, และ recovery ที่ซับซ้อนขึ้น

## 2. สั่งซ่อมนิยายสักตอน

ใช้คำสั่งประมาณนี้:

```text
ช่วยตรวจและซ่อม [ชื่อเรื่อง] ตอน [เลขตอน]
ปัญหาคือ [อธิบายปัญหา]
ให้ทำ 4 อย่าง:
1. ระบุสาเหตุ
2. แก้เฉพาะจุดที่จำเป็น
3. รัน guardrails/Sentinel
4. วางกลไกป้องกันถ้าปัญหานี้อาจเกิดซ้ำ
แล้ว publish MoonRead + commit/push ถ้าแก้ product output
```

ตัวอย่าง:

```text
ช่วยตรวจและซ่อม HGD ตอน 224
ปัญหาคือคำว่า เจ้าสำนัก โผล่มา ทั้งที่ควรเป็นหัวหน้าแผนก
ระบุสาเหตุ แก้ให้ถูก ตรวจ Sentinel แล้วอัป MoonRead + push git
```

ระบบควรทำ:

- เทียบ final output กับ source/artifacts
- ตรวจ glossary ที่เกี่ยวข้อง
- แยกว่าปัญหาเป็นแค่ตอนเดียว, glossary ผิด, prompt/routing ผิด, guardrail ยังจับไม่ได้, หรือ MoonRead generated stale
- ซ่อม output/artifact เท่าที่จำเป็น
- เพิ่ม guardrail/test ถ้าเป็นปัญหาซ้ำได้
- regenerate MoonRead
- verify
- commit/push

ถ้ามีตัวอย่างประโยค ให้ส่งมาด้วย เช่น:

```text
ตอน 203 มีคำว่า “กู” หลุดมา
ควรเป็นเสียงพระเอกสุภาพ ใช้ “ผม”
ช่วยตรวจว่ามีจุดอื่นในช่วงเดียวกันไหม
```

## 3. Setup นิยายเรื่องใหม่

ใช้คำสั่งประมาณนี้:

```text
ช่วย setup นิยายใหม่:
ชื่อเรื่อง: [ชื่อ]
ลิงก์ข้อมูล/รีวิว: [ลิงก์ NovelUpdates หรืออื่นๆ]
ลิงก์ต้นฉบับสำหรับ fetch: [ลิงก์ chapter 1 หรือ index]
ภาษา source: [จีน/อังกฤษ/อื่นๆ ถ้ารู้]
เป้าหมาย: แปลเป็นไทยและขึ้น MoonRead

ให้ทำตาม new novel setup:
- สร้าง/ตรวจ novel profile
- research เรื่องและแนว
- setup fetch adapter/playbook
- fetch raw source ให้ได้มากที่สุดก่อน
- validate chapter sequence
- ทำ Libra - Pilot Gate 20 ตอน
- สรุปปัญหา pipeline
- เสนอ production batch แรก
```

ตัวอย่าง:

```text
ช่วย setup นิยายใหม่

ชื่อ: I'm an Infinite Regressor, But I've Got Stories to Tell
ข้อมูลเรื่อง: https://www.novelupdates.com/series/im-an-infinite-regressor-but-ive-got-stories-to-tell/
ลิงก์ fetch: https://wetriedtls.com/series/im-an-infinite-regressor-but-ive-got-stories-to-tell/chapter-1
เป้าหมาย: แปลไทยและขึ้น MoonRead

fetch ให้ได้มากที่สุดก่อน แล้วทำ Libra - Pilot Gate 20 ตอน
```

ระบบควรทำ:

1. research เรื่อง
2. ทำ novel profile
3. ตรวจแหล่ง fetch
4. fetch raw source
5. ตรวจ chapter gaps
6. สุ่ม 20 ตอนจาก raw source
7. แปล in-sample 10 ตอน
8. วิเคราะห์ปัญหา
9. ปรับ pipeline เฉพาะที่จำเป็น
10. แปล out-of-sample 10 ตอน
11. วัดผลว่าดีขึ้นจริงไหม
12. สรุปว่าเริ่ม production ได้หรือยัง

เหตุผลที่ต้องทำ Pilot Gate: นิยายแต่ละเรื่องมีปัญหาต่างกัน เช่น ชื่อตัวละคร สรรพนาม ระบบเกม ชื่อสกิล title format author note source site แปลก และ chapter gaps

## 4. Publish MoonRead อย่างเดียว

ใช้คำสั่งประมาณนี้:

```text
ช่วยอัป [ชื่อเรื่อง] ตอน [ช่วงตอน] ขึ้น MoonRead
ใช้ generated content จาก output ที่ตรวจแล้ว
รัน publish:verify, Sentinel, lint, build, smoke
แล้ว commit/push
```

## 5. ตรวจคุณภาพหลายตอน

ใช้คำสั่งประมาณนี้:

```text
ช่วย audit คุณภาพ [ชื่อเรื่อง] ตอน [ช่วงตอน]
ตรวจ:
- glossary consistency
- ชื่อตัวละคร
- สรรพนาม
- ภาษาอังกฤษ/จีนหลุด
- paragraph density
- title
- truncation/omission
- MoonRead rendering
ถ้าเจอ pattern ซ้ำ ให้เสนอหรือเพิ่ม guardrail
```

## กฎที่ควรใส่ในคำสั่งงานใหญ่

ใส่ประโยคนี้เสมอ:

```text
ถ้าเจอ manual prompt, QA hard-fail, provider failure, Sentinel blocker/major, หรือ scope หลุด ให้หยุดและรายงานก่อน อย่า force-accept เอง
```

ประโยคนี้ช่วยกันงานเสียแบบเงียบๆ

## รูปแบบคำสั่งที่ดีที่สุด

### แปลต่อ

```text
ช่วยแปล [เรื่อง] [ช่วงตอน] ให้เสร็จ
ใช้ workflow มาตรฐานแบบ bounded batch
แปลเสร็จตรวจ guardrails + Sentinel + spot-check
publish MoonRead และ push git
หยุดถ้าเจอ hard-fail/provider failure/manual prompt
```

### ซ่อมตอน

```text
ช่วยซ่อม [เรื่อง] ตอน [เลขตอน]
ปัญหา: [รายละเอียด]
ให้ระบุสาเหตุ แก้เท่าที่จำเป็น ตรวจซ้ำ เพิ่ม prevention ถ้าควร แล้ว publish/push
```

### Setup เรื่องใหม่

```text
ช่วย setup นิยายใหม่
ชื่อ:
ลิงก์ข้อมูล:
ลิงก์ fetch:
ภาษา source:
เป้าหมาย:
ให้ fetch raw ให้มากที่สุดก่อน แล้วทำ Libra - Pilot Gate 20 ตอน
```

## สถานะระบบที่เหมาะกับการใช้งานตอนนี้

เหมาะกับ:

- แปล batch ละ 5 ตอน
- ซ่อม quality issue แบบมีหลักฐาน
- publish MoonRead
- setup นิยายใหม่แบบมี Pilot Gate
- ตรวจซ้ำด้วย Sentinel/guardrails

ยังไม่ควรใช้กับ:

- แปลยาว 100 ตอนแบบปล่อยไม่เฝ้า
- parallel translate/refine/QA แบบไม่จำกัด
- force-accept QA hard-fail โดยไม่ตรวจ
- publish โดยไม่รัน MoonRead verify

สรุป: ใช้คู่มือนี้เป็นรูปแบบการสั่งงานมาตรฐาน เพื่อให้ระบบทำงานเป็นขั้นตอน ตรวจสอบได้ และลดปัญหาซ้ำระหว่างนิยายหลายเรื่อง
