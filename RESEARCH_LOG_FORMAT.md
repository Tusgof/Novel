# Research Log Format — Novel Translation Pipeline

> **Purpose**: This document defines the exact structure, rules, and conventions for writing research log entries in the **Novel translation pipeline** project.
> When you create or update a research log, you **MUST** follow every rule below. Do not deviate, omit sections, or invent new top-level sections.

---

## 1. File Naming Convention

```
YYYY-MM-DD_<project_slug>_<experiment_or_topic_slug>.md
```

| Token | Rule | Example |
|---|---|---|
| `YYYY-MM-DD` | ISO 8601 date (UTC) of the session | `2026-06-30` |
| `<project_slug>` | Lowercase, underscores, matches project codename | `novel_pipeline` |
| `<experiment_or_topic_slug>` | Lowercase, underscores, brief descriptive slug | `exp07_live_prompt_matrix_v12` |

- If there are multiple revisions on the same date and topic, append `_v<N>` (e.g., `_v2`, `_v3`).
- Store all logs in: `01_Research_Log/`

---

## 2. Timestamp Standard

| Rule | Detail |
|---|---|
| **Reference timezone** | UTC (Coordinated Universal Time, a.k.a. Zulu Time) |
| **Format** | ISO 8601: `YYYY-MM-DDThh:mm:ssZ` |
| **The `T`** | Literal character separating date and time |
| **The `Z`** | Indicates UTC+0 — no local offset applied |
| **24-hour clock** | Always use 24-hour format for `hh:mm:ss` |
| **No DST adjustment** | UTC has no daylight saving time |

### Conversion Example

| Step | Value |
|---|---|
| Local time (Thailand, UTC+7) | `2026-06-30 14:00:00` |
| Subtract 7 hours | `2026-06-30 07:00:00` |
| ISO 8601 output | `2026-06-30T07:00:00Z` |

> **Rule**: Every timestamp field in the log MUST be written in ISO 8601 UTC format.

---

## 3. Document Structure (6 Mandatory Sections)

Every research log file MUST contain exactly these 6 sections, in this order, using the exact heading format shown.

### Section 1 — Title + Metadata

```markdown
# บันทึกการวิจัย: <Descriptive Title in Thai or English>

## 1. ข้อมูลพื้นฐาน

- Timestamp UTC: `<ISO 8601 UTC timestamp>`
- โครงการ: <Project name>
- หัวข้อ: <Short experiment/topic title>
- ผู้บันทึก: <Author or agent name>
- สถานะ: <Current status — e.g., เสร็จสิ้น, อยู่ระหว่างดำเนินการ, ยกเลิก>
```

**Optional metadata fields** (add as needed):

| Field | When to include |
|---|---|
| `เครื่องมือ:` | When specific tools/APIs are used |
| `Model:` | When an LLM model is invoked |
| `Prompt versions:` | When testing multiple prompt variants (use indented list) |
| `Artifact หลัก:` | When the experiment produces output files (use indented list with relative paths) |
| `ผู้ร่วมงาน:` | When collaborating with others |

### Section 2 — Objective

```markdown
## 2. วัตถุประสงค์

<1–3 paragraphs explaining:>
- What question this session aims to answer
- Why this session is needed (link to prior results if applicable)
- What success looks like
```

**Rules**:
- Be specific. Bad: "ทดสอบระบบ". Good: "ทดสอบว่า guarded policy layer จัดการ scheduled macro events ที่เพิ่มมาใหม่ (ISM, JOLTS, retail sales) ได้ถูกต้องหรือไม่"
- If this continues from a prior round, state what the prior round concluded and what gap remains.

### Section 3 — Method & Procedure

```markdown
## 3. วิธีการและขั้นตอน

<Describe what was done, step by step.>
```

**Rules**:
- Use numbered lists for sequential steps.
- Use bullet lists for non-sequential changes.
- Include exact commands in fenced code blocks with the shell language tag (e.g., ` ```powershell `).
- If the method is identical to a prior log, use a cross-reference: "อ้างอิงขั้นตอนจากบันทึก `YYYY-MM-DD_<slug>.md` section 3"
- Specify: tool versions, environment variables set, config files modified, and any parameters changed.

### Section 4 — Results & Raw Data

```markdown
## 4. ผลการศึกษาและข้อมูลดิบ
```

**Rules**:
- Report **all** outcomes — expected AND unexpected.
- Use sub-headings (`###`) to group results by category.
- Reference artifact file paths using relative paths from project root.
- Separate "ผลที่ดี" (positive results) from "ผลที่ยังไม่ผ่าน" (unmet expectations) when applicable.
- Never round numbers without stating the original precision.

**Data Visualization — choose the format that matches data complexity:**

| Data Complexity | Recommended Format | When to Use |
|---|---|---|
| **Simple** (≤5 metrics) | Bullet list with `key: value` | Single-dimension results, e.g., row counts, pass/fail rates |
| **Comparative** (2+ variants side-by-side) | Markdown table | Comparing prompts, strategies, or time periods against the same metrics |
| **Trend / Time-series** | Mermaid `xychart-beta` | Showing how a metric changes across rounds, dates, or parameter sweeps |
| **Distribution / Proportion** | Mermaid `pie` | Showing breakdown of categories, e.g., trade exit reasons |
| **Flow / Process** | Mermaid `flowchart` | Showing decision logic, pipeline stages, or data flow |
| **Narrative** (qualitative) | Prose paragraph | Observations that cannot be reduced to numbers |

**Visualization examples:**

Comparative table (e.g., multi-strategy PnL):
```markdown
| Metric | forced_close_only | target_stop_25_50 |
|---|---|---|
| Closed trades | 2 | 2 |
| Total net PnL | -$1.00 | -$12.00 |
| Win rate | 0.50 | 0.50 |
| Max drawdown | -0.001998 | -0.019841 |
```

Trend chart (e.g., stability across experiment rounds):
```markdown
```mermaid
xychart-beta
  title "Guarded Stable Cases by Round"
  x-axis [v8, v9, v10, v11, v12]
  y-axis "Cases" 0 --> 50
  bar [28, 30, 33, 35, 43]
`` `
```

Distribution chart (e.g., exit type breakdown):
```markdown
```mermaid
pie title Trade Exit Reasons
  "Profit Target" : 1
  "Stop Loss" : 1
`` `
```

> **Rule**: When results contain **3+ comparable dimensions** or **trend data across rounds**, you MUST use a table or Mermaid chart instead of a plain bullet list. Choose the simplest format that makes the pattern immediately visible.

### Section 5 — Issues & Troubleshooting

```markdown
## 5. ปัญหา อุปสรรค และการแก้ไข
```

**Rules**:
- Record every problem encountered, even if trivial.
- For each problem, document:
  1. **What happened** (symptom)
  2. **How it was resolved** (action taken)
  3. **Outcome after resolution** (did it work?)
- If no problems occurred, write: "ไม่พบปัญหาในรอบนี้"
- Add a "ข้อจำกัดสำคัญ" (key limitations) sub-section if the results have caveats that affect interpretation.

### Section 6 — Conclusion & Next Steps

```markdown
## 6. ข้อสรุปและก้าวต่อไป
```

**Rules**:
- Start with a one-sentence verdict: "ข้อสรุป: <summary judgment>"
- Follow with bullet-point reasoning that supports the verdict.
- End with a numbered list of concrete next steps, ordered by priority.
- Each next step must be actionable (a verb phrase), not vague.
  - Bad: "ศึกษาเพิ่มเติม"
  - Good: "ขยาย in-sample coverage ไปยัง Aug 2023 โดยทำ cost estimate ก่อน download"

## 4. Quick-Reference Template

Copy this template when starting a new research log:

```markdown
# บันทึกการวิจัย: <TITLE>

## 1. ข้อมูลพื้นฐาน

- Timestamp UTC: `YYYY-MM-DDThh:mm:ssZ`
- โครงการ: Novel Translation Pipeline
- หัวข้อ: <topic>
- ผู้บันทึก: <author>
- สถานะ: <status>

## 2. วัตถุประสงค์

<What question does this session answer? Why now? What does success look like?>

## 3. วิธีการและขั้นตอน

<Step-by-step procedure. Include commands, configs, and tool versions.>

## 4. ผลการศึกษาและข้อมูลดิบ

<All outcomes with numbers, file references, and structured data.>

## 5. ปัญหา อุปสรรค และการแก้ไข

<Every problem + resolution. Or: "ไม่พบปัญหาในรอบนี้">

## 6. ข้อสรุปและก้าวต่อไป

ข้อสรุป: <one-sentence verdict>

<Reasoning bullets>

ก้าวต่อไป:
1. <actionable next step>
2. <actionable next step>
```

---
---

# Part 2: Operational Rules — กฎการทำงานและการใช้ Research Log

> **Purpose**: This section defines **when** to write a log, **what to do after** writing it, and **behavioral constraints** the AI author must follow at all times. These rules are separate from the format specification above and apply to the overall workflow.

---

## 5. Workflow Triggers — เมื่อไหร่ต้องเขียน Research Log

| # | Trigger | Action |
|---|---|---|
| 1 | **เสร็จสิ้น 1 การทดลอง (experiment round)** | สร้าง research log ใหม่ 1 ไฟล์ตาม format ใน Part 1 ทันที |
| 2 | **ยกเลิกการทดลองระหว่างทาง** | สร้าง research log เช่นกัน โดยระบุสถานะ: `ยกเลิก` พร้อมเหตุผลใน Section 5 |
| 3 | **แก้ไขหรือเพิ่มเติมผลการทดลองเดิม** | อัปเดตไฟล์ log เดิม (ไม่สร้างไฟล์ใหม่) และเพิ่มหมายเหตุว่าแก้ไขอะไร เมื่อไหร่ |

> **Rule**: ห้ามรอจนจบหลายการทดลองแล้วค่อยเขียนรวม — **1 การทดลอง = 1 research log** เสมอ

---

## 6. Post-Write Workflow — ขั้นตอนหลังเขียน Research Log เสร็จ

เมื่อเขียนหรืออัปเดต research log เสร็จ **ทุกครั้ง** ต้องทำตามขั้นตอนนี้:

### Step 1: Verify the log file

ตรวจสอบว่าไฟล์ log:
- อยู่ใน `01_Research_Log/` directory (full path: `D:\Fogust\Workspace\Novel\01_Research_Log`)
- ชื่อไฟล์ตรงตาม naming convention
- มีครบทั้ง 6 sections

### Step 2: Commit and push to GitHub

```powershell
cd D:\Fogust\Workspace\Novel
git add 01_Research_Log/
git commit -m "research-log: <short description of experiment>"
git push origin main
```

| Field | Rule |
|---|---|
| **Remote repository** | `https://github.com/Tusgof/Novel.git` |
| **Branch** | `main` (unless instructed otherwise) |
| **Commit message format** | `research-log: <brief experiment description in English>` |
| **Push timing** | Immediately after writing/updating the log — do NOT batch multiple logs |

### Step 3: Confirm push success

- Verify `git push` exits without error.
- If push fails (auth, network, conflict), report the error to the user immediately and do NOT proceed to other tasks until resolved.

> **Rule**: Research log ที่ยังไม่ได้ push ขึ้น GitHub ถือว่า **ยังไม่เสร็จสมบูรณ์**

---

## 7. Behavioral Rules for the AI Author

These rules apply whenever you are writing or updating a research log.

| # | Rule |
|---|---|
| 1 | **Record in real-time.** Write findings as they happen. Do not reconstruct from memory after the fact. |
| 2 | **Never delete mistakes.** If an experiment fails or a value is wrong, keep the record and annotate it. Failures are data. |
| 3 | **Never fabricate data.** If a metric was not measured, write "ไม่ได้วัด" — never invent a number. |
| 4 | **Use UTC timestamps everywhere.** No local time without explicit conversion shown. |
| 5 | **Reference, don't duplicate.** If a procedure was documented before, cross-reference the prior log instead of copying it. |
| 6 | **Keep raw data links.** Always include relative paths to any output files (JSON, JSONL, CSV, reports). |
| 7 | **One log per session or experiment round.** Do not merge unrelated experiments into one file. |
| 8 | **Language consistency.** Section headings are in Thai (as shown above). Body text may be Thai or English, but be consistent within each section. |
| 9 | **No speculation without labeling.** If you interpret data beyond what the numbers show, prefix with "สมมติฐาน:" or "การตีความ:". |
| 10 | **Follow the naming convention.** Every file name must match the pattern in Section 1 of this document. |
| 11 | **Always push after writing.** Follow the Post-Write Workflow (Section 6) after every log creation or update. |
