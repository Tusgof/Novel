# บันทึกการวิจัย: V6.34 M6 IRS OOS Completion

## 1. ข้อมูลพื้นฐาน

- Timestamp UTC: `2026-07-01T13:58:15Z`
- โครงการ: Novel Translation Pipeline
- หัวข้อ: V6.34 M6 IRS out-of-sample completion
- ผู้บันทึก: Codex
- สถานะ: เสร็จสิ้น
- Artifact หลัก:
  - `07_Reports/v6_34_m6_irs_oos_completion_20260701.md`
  - `Infinite Regressor Stories/04_Work/_experiments/v6_34_m6_irs_oos_v1/06_Logs/run_ledger.jsonl`
  - `Infinite Regressor Stories/04_Work/_experiments/v6_34_m6_irs_oos_v1/07_Reports/sentinel_quality_v6-34-m6-irs-oos-v1_ch*_sentinel_20260701_*.md`

## 2. วัตถุประสงค์

รอบนี้มีเป้าหมายเพื่อปิด out-of-sample measurement ของ Infinite Regressor Stories ใน V6.34 หลังจาก HGD และ DSE OOS จบแล้ว โดยต้องยืนยันว่าสถานะจบจริงจาก ledger, source parity, deterministic output checks, และ Sentinel ไม่ใช่เชื่อจาก provider report อย่างเดียว

ความสำเร็จของรอบนี้คือ IRS OOS ต้องจบครบทุก locked chapter ใน isolated experiment vault, ไม่มี current failed block, ไม่มี source mismatch, ไม่มี blocker/major จาก Sentinel, และไม่มี output-surface leakage ที่เคยเป็นปัญหา เช่น CJK/Hanja, Thai numeral, provider/meta text, หรือ title-like body paragraph

## 3. วิธีการและขั้นตอน

1. ตรวจสถานะ run ระหว่างที่ `novel-pipeline resume` ยังทำงานอยู่ เพื่อแยก historical provider failure ออกจาก current blocker

```powershell
cd "D:\Fogust\Workspace\Novel\Infinite Regressor Stories\04_Work\_experiments\v6_34_m6_irs_oos_v1"
$env:PYTHONIOENCODING='utf-8'
novel-pipeline --config ".system/config.yaml" resume --run-id v6-34-m6-irs-oos-v1 --manual-action-mode stop
```

2. หลัง run จบ ตรวจสถานะด้วย CLI

```powershell
novel-pipeline --config ".system/config.yaml" status --run-id v6-34-m6-irs-oos-v1
```

3. ตรวจ source parity จาก root workspace

```powershell
cd "D:\Fogust\Workspace\Novel"
$env:PYTHONIOENCODING='utf-8'
python scripts\verify_experiment_source_parity.py --novel-root "Infinite Regressor Stories" --experiment-root "Infinite Regressor Stories\04_Work\_experiments\v6_34_m6_irs_oos_v1" --chapters "ch012,ch053,ch095,ch144,ch187,ch208,ch258,ch290,ch323,ch372"
```

4. ตรวจ deterministic experiment-output ด้วย scoped inline audit เพราะ shared product guardrail script ผูกกับ production registry paths ไม่ใช่ experiment vault paths

5. อ่าน Sentinel reports ใน experiment vault เพื่อยืนยันว่าแต่ละ chapter มี blocker/major/minor/info `0/0/0/0`

## 4. ผลการศึกษาและข้อมูลดิบ

### ผลที่ดี

| Metric | Result |
|---|---:|
| Locked OOS chapters | 10 |
| Completed chapters | 10 |
| Completed blocks | 33/33 |
| Current failed blocks | 0 |
| Manual actions needed | 0 |
| Source parity mismatches | 0 |
| Deterministic output issues | 0 |
| Latest scoped Sentinel blocker/major/minor/info | 0/0/0/0 for all 10 chapters |

### Provider / smoothness evidence

| Stage | Provider / model | Count |
|---|---:|---:|
| translating completed | openrouter | 33 |
| refining completed | openrouter | 45 |
| refining failed | openrouter `deepseek/deepseek-v4-flash` | 2 |
| refining completed | local_recovery | 2 |
| qa completed | openrouter `deepseek/deepseek-v4-flash` | 30 |
| qa completed | openrouter `google/gemini-3-flash-preview` | 3 |
| formatting completed | openrouter `deepseek/deepseek-v4-flash` | 22 |
| formatting completed | openrouter `google/gemini-3-flash-preview` | 7 |
| formatting completed | local | 4 |
| sentinel completed | local | 10 |

### ผลที่ยังไม่ผ่าน / ข้อสังเกต

- มี historical provider failure 2 records ระหว่าง refining:
  - `ch208-block-002`: OpenRouter returned an empty assistant message
  - `ch290-block-002`: OpenRouter returned an empty assistant message
- ทั้งสองจุด recover ได้และ block จบสมบูรณ์ แต่เป็นหลักฐานว่า long-run smoothness ยังไม่ควรถูกมองว่าสมบูรณ์
- IRS OOS ไม่พบการเกิดซ้ำของ CJK/Hanja parenthetical hard-fail และไม่พบ `Complete Memory` minor miss ในรอบนี้

## 5. ปัญหา อุปสรรค และการแก้ไข

1. ปัญหา: ระหว่าง run มี OpenRouter refining failure 2 ครั้งจาก empty assistant message
   - วิธีแก้: pipeline recovery/fallback ดำเนินต่อจน block completed
   - ผลลัพธ์: current failed blocks เป็น `0` แต่บันทึกเป็น smoothness risk

2. ปัญหา: การเรียก `scripts/check_output_quality_guardrails.py` จาก experiment vault โดยตรงล้มเหลว เพราะ script ไม่อยู่ใน vault และ shared guardrail ผูก production paths
   - วิธีแก้: ใช้ scoped inline audit กับ experiment `05_Output` โดยตรง
   - ผลลัพธ์: ตรวจครบ 10 chapters และพบ issues `0`

3. ปัญหา: inline Thai numeral check รุ่นแรกใช้ regex/literal ที่ PowerShell encoding ทำให้จับ `ๆ` หรือ `?` ผิดเป็นเลขไทย
   - วิธีแก้: เปลี่ยนเป็นการเทียบ codepoint `0x0E50` ถึง `0x0E59`
   - ผลลัพธ์: ยืนยันว่า experiment outputs ไม่มี Thai numerals จริง

## 6. ข้อสรุปและก้าวต่อไป

ข้อสรุป: IRS OOS ผ่านในแง่ final output quality แต่ยังแสดง provider smoothness risk จาก empty assistant message ระหว่าง refining

- IRS OOS จบครบ 10 chapters และ 33 blocks โดยไม่มี current failed block
- Source parity เป็น `0` จึงใช้เป็น measurement data ได้
- Deterministic output checks และ Sentinel latest reports ผ่านทั้งหมด
- Provider failures ที่ recover ได้ยังควรนับใน M6 cross-novel comparison เพราะเป้าหมาย V6.34 ไม่ใช่แค่ output ผ่าน แต่ต้องวัดความยั่งยืนของ long-run execution ด้วย

ก้าวต่อไป:
1. ทำ V6.34 M6 cross-novel OOS comparison โดยรวม HGD, DSE, และ IRS
2. สรุป production recommendation ว่าควรใช้ bounded sequential, bounded parallel slice, หรือยังไม่พร้อม scale
3. อัปเดต `PROJECT_BRAIN.md` และ `IMPLEMENT_PLAN.md` หลัง comparison เสร็จ
4. หลัง V6.34 ปิดครบแล้ว จึงพิจารณางาน production ถัดไปของ DSE ถึง `ch210`
