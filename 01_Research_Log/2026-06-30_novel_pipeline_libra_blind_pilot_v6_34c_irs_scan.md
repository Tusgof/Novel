# บันทึกการวิจัย: V6.34C IRS In-Sample Scan-Only Gate

## 1. ข้อมูลพื้นฐาน

- Timestamp UTC: `2026-06-30T20:44:48Z`
- โครงการ: Novel Translation Pipeline
- หัวข้อ: V6.34C IRS high-risk in-sample scan-only gate
- ผู้บันทึก: Codex
- สถานะ: เสร็จสิ้นสำหรับรอบ scan-only; ยังไม่เริ่ม translation treatment
- Artifact หลัก:
  - `Infinite Regressor Stories/04_Work/_experiments/v6_34c_irs_insample_v1/`
  - `Infinite Regressor Stories/04_Work/_experiments/v6_34c_irs_insample_v1/04_Work/_batch/v6-34c-irs-insample-v1/glossary_scan.json`
  - `Infinite Regressor Stories/04_Work/_experiments/v6_34c_irs_insample_v1/06_Logs/run_ledger.jsonl`

## 2. วัตถุประสงค์

รอบนี้ทดสอบขั้นแรกของ V6.34C สำหรับ IRS in-sample wave จาก raw-source sample ที่สุ่มไว้ ไม่ใช่จากตอนที่เลือกเพราะเคยมีปัญหา เป้าหมายคือยืนยันว่า pipeline สามารถสร้าง isolated experiment vault, รัน scan-only gate, และผลิต glossary candidate artifact สำหรับตอน high-risk ได้โดยไม่แตะ production output หรือ MoonRead

ความสำเร็จของรอบนี้คือ scan-only ต้องหยุดที่ glossary scan, ledger ต้องมีเฉพาะ `fetched` และ `glossary_scanned`, ไม่มี translation/refinement/QA/formatting/final output, และ artifact ต้องมี candidate terms พอสำหรับรอบ classification/approval ถัดไป

## 3. วิธีการและขั้นตอน

1. สร้าง isolated experiment vault:

```powershell
Infinite Regressor Stories/04_Work/_experiments/v6_34c_irs_insample_v1
```

2. Copy เฉพาะไฟล์ที่จำเป็นเข้า experiment vault:

- `.system/`
- `01_Glossary/`
- `03_Raw/` เฉพาะ IRS in-sample 10 ตอน
- `prompts/`
- `scripts/openrouter_provider_shim.py`
- `NOVEL_PROFILE.yaml`
- `RESEARCH_PROFILE.yaml`

3. แก้เฉพาะ experiment copy ของ `.system/providers.yaml` ให้ Codex fallback `--cd` ชี้ experiment vault แทน production IRS root

4. รัน preflight จาก experiment vault:

```powershell
novel-pipeline --config ".system/config.yaml" preflight
```

5. รัน scan-only gate:

```powershell
$env:PYTHONIOENCODING='utf-8'
novel-pipeline --config ".system/config.yaml" run --range "ch009,ch076,ch086,ch157,ch183,ch201,ch252,ch300,ch338,ch381" --run-id v6-34c-irs-insample-v1 --stop-after glossary-scan
```

6. ตรวจ status และสรุป artifact:

```powershell
novel-pipeline --config ".system/config.yaml" status --run-id v6-34c-irs-insample-v1
```

## 4. ผลการศึกษาและข้อมูลดิบ

### ผลที่ดี

| Metric | Result |
|---|---:|
| Chapters scanned | 10 |
| Ledger records | 20 |
| `fetched` records | 10 |
| `glossary_scanned` records | 10 |
| Candidate items | 175 |
| Translation/refinement/QA/formatting records | 0 |
| Current failed blocks | 0 |
| Final outputs created | 0 |

### Candidate breakdown

| Dimension | Value |
|---|---|
| Chapters | `ch009,ch076,ch086,ch157,ch183,ch201,ch252,ch300,ch338,ch381` |
| Categories | `character: 6`, `entity: 7`, `location: 1`, `term: 151`, `title: 8`, `vessel: 2` |
| By chapter | `ch009: 28`, `ch076: 22`, `ch086: 10`, `ch157: 16`, `ch183: 10`, `ch201: 15`, `ch252: 24`, `ch300: 29`, `ch338: 18`, `ch381: 3` |

### First 30 candidate terms

`The Awakeners`, `Brother Undertaker`, `East Asia`, `East Asian`, `华山`, `北京`, `仁川`, `天津港`, `送葬者`, `北京攻略指南`, `黄海`, `觉醒者`, `北京地铁`, `北京解放突击队`, `次渠站`, `普洱茶`, `孔孟之道`, `圣女`, `千里眼`, `天坛公园`, `天坛东门站`, `天坛`, `National Salvation`, `龙之升华`, `回归魔`, `救国圣女`, `决定论者`, `蝴蝶效应`, `Magical Girl Association`, `The Magical Girls`

### Current status after scan

Status reports all selected chapters pending `translating`, with no failed blocks. Block count estimate:

- `ch009`: 3 blocks
- `ch076`: 3 blocks
- `ch086`: 3 blocks
- `ch157`: 3 blocks
- `ch183`: 3 blocks
- `ch201`: 3 blocks
- `ch252`: 4 blocks
- `ch300`: 3 blocks
- `ch338`: 4 blocks
- `ch381`: 3 blocks
- Total: 32 pending translation blocks

## 5. ปัญหา อุปสรรค และการแก้ไข

1. Symptom: preflight reported `degraded` because the root working tree was dirty.
   - Action: kept the run bounded and isolated; did not start production output work.
   - Outcome: scan-only succeeded without writing to production `05_Output` or MoonRead.

2. Symptom: initial artifact summary script read `.candidates`, but `glossary_scan.json` uses `items`.
   - Action: inspected JSON schema and summarized `items` instead.
   - Outcome: candidate count corrected to 175.

3. Symptom: provider config copy originally risked keeping Codex fallback cwd pointed at production IRS root.
   - Action: patched only the experiment copy so `--cd` points at `v6_34c_irs_insample_v1`.
   - Outcome: experiment provider fallback context is isolated from production.

ข้อจำกัดสำคัญ:

- This round is scan-only. It does not prove translation/refinement/QA/formatting quality yet.
- The 175 candidates have not been classified or approved.
- No output guardrail or Sentinel translation-output check is applicable yet because no experiment outputs were created.

## 6. ข้อสรุปและก้าวต่อไป

ข้อสรุป: V6.34C IRS in-sample scan-only gate passed and produced a large glossary candidate set without touching production outputs.

- The isolated experiment approach worked and should remain the default for V6.34 treatment waves.
- IRS late/high-risk chapters produce substantial glossary pressure, including mixed English, Chinese, title, entity, and term candidates.
- The next risk is glossary classification quality: 175 candidates is too large for ad hoc approval and should be classified before any translation resume.

ก้าวต่อไป:

1. Classify the 175 IRS glossary candidates into approve/reject/ask-human groups inside the experiment context.
2. Approve only high-value recurring terms, entities, titles, and system/story terms needed for the 10 selected chapters.
3. Append experiment-local `glossary_approved` records only after classification.
4. Resume the IRS in-sample experiment translation from `v6-34c-irs-insample-v1` after glossary approval.
5. Record the translation treatment as a separate research log round.

