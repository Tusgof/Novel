# บันทึกการวิจัย: V6.34C IRS Glossary Approval

## 1. ข้อมูลพื้นฐาน

- Timestamp UTC: `2026-06-30T20:56:14Z`
- โครงการ: Novel Translation Pipeline
- หัวข้อ: V6.34C IRS experiment-local glossary approval
- ผู้บันทึก: Codex
- สถานะ: เสร็จสิ้น
- Artifact หลัก:
  - `07_Reports/v6_34c_irs_glossary_approval_decisions_20260701.md`
  - `Infinite Regressor Stories/04_Work/_experiments/v6_34c_irs_insample_v1/07_Reports/v6_34c_irs_glossary_approval_packet.json`
  - `Infinite Regressor Stories/04_Work/_experiments/v6_34c_irs_insample_v1/06_Logs/run_ledger.jsonl`

## 2. วัตถุประสงค์

รอบนี้นำผล classification จาก V6.34C IRS glossary scan มาทำ approval แบบ experiment-local เพื่อให้ translation treatment รอบถัดไปมี glossary context ที่ดีกว่าเดิมโดยไม่แตะ production glossary

ความสำเร็จคือ experiment vault ต้องมี glossary notes/aliases ที่จำเป็น, ledger ต้องมี `glossary_approved` ครบ 10 chapters, และยังต้องไม่มี translation/refinement/QA/formatting records

## 3. วิธีการและขั้นตอน

1. ตรวจ source-aware candidates จาก classification report
2. ตรวจ exact occurrence ของ CJK candidates ใน raw source
3. Reject CJK candidates ที่ไม่ปรากฏใน raw source จริง
4. สร้าง experiment-local glossary notes และ alias updates ใน:

```powershell
Infinite Regressor Stories/04_Work/_experiments/v6_34c_irs_insample_v1/01_Glossary/
```

5. บันทึก approval packet:

```powershell
Infinite Regressor Stories/04_Work/_experiments/v6_34c_irs_insample_v1/07_Reports/v6_34c_irs_glossary_approval_packet.json
```

6. Commit batch approval records:

```powershell
cd "D:\Fogust\Workspace\Novel\Infinite Regressor Stories\04_Work\_experiments\v6_34c_irs_insample_v1"
$env:PYTHONIOENCODING='utf-8'
novel-pipeline --config ".system/config.yaml" approve-terms --batch --run-id v6-34c-irs-insample-v1 --decision-report "07_Reports/v6_34c_irs_glossary_approval_decisions_20260701.md"
```

7. Verify status:

```powershell
novel-pipeline --config ".system/config.yaml" status --run-id v6-34c-irs-insample-v1
```

## 4. ผลการศึกษาและข้อมูลดิบ

| Metric | Result |
|---|---:|
| New experiment-local notes | 73 |
| Existing experiment-local notes updated with aliases | 7 |
| `glossary_approved` records | 10 |
| Translation/refinement/QA/formatting records | 0 |
| Current failed blocks | 0 |
| Production glossary files changed | 0 |
| Production output/MoonRead files changed | 0 |

Approved block IDs:

`ch009`, `ch076`, `ch086`, `ch157`, `ch183`, `ch201`, `ch252`, `ch300`, `ch338`, `ch381`

## 5. ปัญหา อุปสรรค และการแก้ไข

1. Symptom: CJK candidates looked important but did not appear in the raw English source.
   - Action: exact-source check was run for every CJK candidate.
   - Outcome: CJK candidates were rejected for this experiment instead of becoming glossary notes.

2. Symptom: Some useful variants should not become duplicate notes.
   - Action: variants such as `The Awakeners`, `The Undertaker`, and faction-member phrases were attached as aliases.
   - Outcome: glossary duplication risk is lower for the treatment run.

3. Symptom: One alias string suffered shell encoding degradation during packet generation.
   - Action: normalized the Baekhwa spelling alias to ASCII apostrophe form.
   - Outcome: experiment-local note now contains stable spelling variants without mojibake.

ข้อจำกัดสำคัญ:

- These approvals are experiment-local. They should not be promoted to production IRS glossary until V6.34C treatment and later OOS evidence prove they improve quality.
- The run is now ready to translate, but translation treatment is a separate experiment round.

## 6. ข้อสรุปและก้าวต่อไป

ข้อสรุป: V6.34C IRS experiment-local glossary approval is complete and the isolated run is ready for translation treatment.

- Approval records exist for all 10 selected chapters.
- Production glossary/output/MoonRead were not modified.
- The key pipeline lesson is that AI glossary scan can infer non-source CJK terms; exact-source validation should become a candidate-filtering improvement before approval UI.

ก้าวต่อไป:

1. Resume `v6-34c-irs-insample-v1` in the isolated experiment vault.
2. Stop on the first provider/manual/QA/Sentinel failure and record it as treatment evidence.
3. After translation treatment, run output guardrails and Sentinel for experiment outputs.
4. Record treatment results in a separate research log.

