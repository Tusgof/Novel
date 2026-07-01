# บันทึกการวิจัย: V6.34 M6 Cross-Novel OOS Comparison

## 1. ข้อมูลพื้นฐาน

- Timestamp UTC: `2026-07-01T14:05:00Z`
- โครงการ: Novel Translation Pipeline
- หัวข้อ: V6.34 M6 cross-novel OOS comparison and production recommendation
- ผู้บันทึก: Codex
- สถานะ: เสร็จสิ้น
- Artifact หลัก:
  - `07_Reports/v6_34_m6_cross_novel_oos_comparison_20260701.md`
  - `07_Reports/v6_34_m6_hgd_oos_completion_20260701.md`
  - `07_Reports/v6_34_m6_dse_oos_completion_20260701.md`
  - `07_Reports/v6_34_m6_irs_oos_completion_20260701.md`

## 2. วัตถุประสงค์

รอบนี้มีเป้าหมายเพื่อรวมผล OOS ของ HGD, DSE, และ IRS แล้วตอบคำถามหลักของ V6.34 ว่า treatment ที่ทำมาตั้งแต่ baseline/in-sample ช่วยให้ pipeline ดีขึ้นพอสำหรับ production mode แบบใด

ความสำเร็จของรอบนี้ไม่ใช่การประกาศว่าระบบสมบูรณ์แบบ แต่ต้องให้ recommendation ที่มีหลักฐาน: อะไรปลอดภัยพอให้ใช้ต่อ, อะไรยังไม่ควรเปิด, และความเสี่ยงไหนต้องคุมใน production batch ถัดไป

## 3. วิธีการและขั้นตอน

1. ใช้รายงาน OOS completion ของแต่ละเรื่องเป็น evidence base:
   - HGD: `07_Reports/v6_34_m6_hgd_oos_completion_20260701.md`
   - DSE: `07_Reports/v6_34_m6_dse_oos_completion_20260701.md`
   - IRS: `07_Reports/v6_34_m6_irs_oos_completion_20260701.md`
2. เทียบ metrics ที่ล็อกไว้ใน V6.34 measurement contract:
   - completed chapters/blocks
   - current failed blocks
   - source parity
   - Sentinel blocker/major/minor/info
   - deterministic output guardrails
   - provider failures
   - QA hard-fails
   - manual/recovery work
3. สรุป hypothesis verdict โดยแยก output quality ออกจาก smoothness
4. สร้าง production recommendation โดยไม่ publish experiment output

## 4. ผลการศึกษาและข้อมูลดิบ

| Metric | HGD OOS | DSE OOS | IRS OOS |
|---|---:|---:|---:|
| Completed chapters | 10/10 | 10/10 | 10/10 |
| Completed blocks | 10/10 | 55/55 | 33/33 |
| Current failed blocks | 0 | 0 | 0 |
| Manual actions needed | 0 | 0 | 0 |
| Final source parity | 0 | 0 | 0 |
| Latest Sentinel blocker/major | 0/0 | 0/0 | 0/0 |
| Deterministic output issues | 0 | 0 | 0 |
| Historical provider failures | 1 | not highlighted in valid completion evidence | 2 |
| QA hard-fails during OOS | 2 | 1 | 0 |
| Sentinel stops during OOS | 1 | 0 | 0 |

ผลเชิงคุณภาพ:

- Output-surface quality ผ่านในทั้ง 3 เรื่องหลัง treatment/recovery ที่ถูกต้อง
- Source parity กลายเป็น gate สำคัญ เพราะ DSE v1 แสดงให้เห็นว่า vault ที่ copy มาอาจ stale/off-by-one ได้
- IRS OOS ไม่พบการเกิดซ้ำของ CJK/Hanja parenthetical leakage หรือ `Complete Memory` minor miss
- Smoothness ยังไม่ผ่านเกณฑ์ long unattended run เพราะ HGD และ IRS ยังมี failure/recovery evidence

## 5. ปัญหา อุปสรรค และการแก้ไข

1. ปัญหา: DSE OOS v1 ใช้ stale/off-by-one raw source
   - วิธีแก้: rebuild vault และใช้ source parity gate
   - ผลลัพธ์: DSE OOS v2 parity `0` และ measurement valid

2. ปัญหา: HGD OOS เจอ glossary conflict, false glossary match, semantic drift, และ pronoun drift
   - วิธีแก้: เพิ่ม source-surface collision detection, boundary-aware glossary matching, และ HGD-only peer-address treatment
   - ผลลัพธ์: HGD OOS จบครบและ Sentinel latest `0/0/0/0`

3. ปัญหา: IRS OOS ยังมี OpenRouter empty-assistant refining failures
   - วิธีแก้: pipeline recovery/fallback จัดการจน block complete
   - ผลลัพธ์: output ผ่าน แต่ smoothness risk ยังต้องคงไว้

## 6. ข้อสรุปและก้าวต่อไป

ข้อสรุป: V6.34 สนับสนุนให้เดิน production ต่อแบบ bounded sequential batch แต่ยังไม่สนับสนุน long unattended หรือ broad parallel production

- คุณภาพ final output หลัง guardrail/Sentinel ดีขึ้นจริงใน OOS ทั้ง 3 เรื่อง
- ปัญหา recurring หลายจุดถูกย้ายเป็น prevention ที่ถูก layer มากขึ้น
- ความเสถียรของ provider/recovery ยังไม่ดีพอให้ปล่อยรันยาวโดยไม่ monitor
- DSE production continuation ถึง `ch210` ทำได้เป็นงานถัดไป แต่ต้องถือเป็น bounded batch พร้อม stop conditions เดิม

ก้าวต่อไป:
1. อัปเดต `PROJECT_BRAIN.md` และ `IMPLEMENT_PLAN.md` ให้ V6.34 M6 comparison เสร็จ
2. ปิด V6.34 documentation/finalization
3. ก่อนเริ่ม DSE production ต่อ ให้ verify ว่า range ที่ถูกต้องคือ `ch181-ch210` จำนวน 30 chapters ไม่ใช่ 29
4. เริ่ม DSE continuation แบบ bounded sequential หลังเอกสารและ git state สะอาด
