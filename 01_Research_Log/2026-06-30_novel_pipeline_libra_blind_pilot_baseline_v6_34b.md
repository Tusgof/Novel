# บันทึกการวิจัย: V6.34B Cross-Novel Read-Only Baseline

## 1. ข้อมูลพื้นฐาน

- Timestamp UTC: `2026-06-30T20:31:00Z`
- โครงการ: Novel Translation Pipeline
- หัวข้อ: V6.34B read-only baseline analyzers for the 60-chapter blind sample
- ผู้บันทึก: Codex
- สถานะ: เสร็จสิ้น
- Artifact หลัก:
  - `07_Reports/v6_34b_cross_novel_baseline_risk_table_20260630_203000.json`
  - `07_Reports/v6_34b_cross_novel_baseline_risk_table_20260630_203000.md`

## 2. วัตถุประสงค์

รอบนี้ตอบคำถามว่า sample 60 ตอนจาก V6.34A มีความเสี่ยงเชิง source/prompt/glossary อย่างไร ก่อนเริ่ม provider-backed translation

เป้าหมายคือสร้าง baseline ที่วัดได้จาก `03_Raw/` เท่านั้น เพื่อระบุว่าตอนไหนควรระวังเรื่องความยาว, bracket/system UI, repeated characters, footnote/author-note markers, title sidecar, และ glossary density โดยไม่เรียก provider และไม่แตะ production artifacts

## 3. วิธีการและขั้นตอน

1. ใช้ chapter sample จาก V6.34A seed `634001`
2. โหลด source จาก `03_Raw/<chapter>/source.json` ของทั้ง 3 นิยาย
3. โหลด approved glossary notes จาก `01_Glossary/*.md` ของแต่ละนิยาย
4. วิเคราะห์แบบ read-only:
   - source character count
   - bracket/system-message density
   - repeated-character risk
   - footnote/author-note marker risk
   - title-sidecar risk
   - approved glossary hit count
   - embedded CJK/Hangul/Thai source risk
5. เขียน raw data เป็น JSON และ Markdown report

คำสั่งหลัก:

```powershell
python - <<'PY'
# Inline read-only analyzer over V6.34A selected raw-source chapters.
# Writes 07_Reports/v6_34b_cross_novel_baseline_risk_table_20260630_203000.{json,md}
PY
```

## 4. ผลการศึกษาและข้อมูลดิบ

### Artifact

| Artifact | Purpose |
| --- | --- |
| `07_Reports/v6_34b_cross_novel_baseline_risk_table_20260630_203000.json` | Raw machine-readable per-chapter metrics |
| `07_Reports/v6_34b_cross_novel_baseline_risk_table_20260630_203000.md` | Human-readable summary and table |

### Summary

| Novel | Rows | Missing source | Glossary terms loaded | Main findings |
| --- | ---: | ---: | ---: | --- |
| Deep Sea Embers | 20 | 0 | 168 | title sidecar required on 20/20; glossary density high on 20/20; footnote/author-note heuristic flagged 18/20 |
| Horror Game Developer | 20 | 0 | 297 | glossary density high on 14/20; bracket/system density on 2/20; one long source |
| Infinite Regressor Stories | 20 | 0 | 363 | highest risk: 9 very-long sources, 11 long sources, 6 high-bracket chapters, 17 footnote/author-note markers, 7 very-high glossary density |

### Highest-Risk Observations

IRS dominates the high-risk list. Highest-risk examples:

| Novel | Chapter | Split | Main risk |
| --- | --- | --- | --- |
| IRS | `ch133` | out-of-sample | long source, bracket density, repeated-character risk, footnote/author-note marker, very-high glossary density, embedded CJK |
| IRS | `ch093` | out-of-sample | very long source, Hangul and embedded CJK risk |
| IRS | `ch009` | in-sample | very long source, high bracket density, very-high glossary density |
| IRS | `ch278` | out-of-sample | long source, high bracket density, repeated-character risk, very-high glossary density |
| DSE | `ch150` | in-sample | very-high glossary density and title sidecar requirement |

### Interpretation

การตีความ: V6.34C ไม่ควรเริ่มด้วยการรันทั้ง 30 in-sample พร้อมกัน ควรเริ่มเป็น 3 wave ตาม novel และเริ่มจาก high-risk IRS in-sample chapters เพื่อวัดว่ากลไกปัจจุบันรับ source ยาวและ glossary density ได้จริงหรือไม่

การตีความ: DSE title-sidecar requirement เป็น expected policy ไม่ใช่ bug แต่ต้องยืนยันว่า experiment output ไม่ fallback เป็น `บทที่ N`

ข้อจำกัด: `footnote_or_author_note_risk` เป็น heuristic ที่อาจ false positive โดยเฉพาะ DSE เพราะตัวอักษรจีนบางตัวตรงกับ marker pattern จึงใช้เป็น signal สำหรับ inspection ไม่ใช่ blocker

### Layer Classification

| Finding class | Layer | Rationale |
| --- | --- | --- |
| Missing source check and stratified raw-source sampling | Layer 0 multi-novel | Applies to every novel before any pilot or production batch |
| Long/very-long source pressure | Layer 0 multi-novel | Should drive shared block-splitting and provider-timeout policy |
| High glossary density | Layer 0 multi-novel + Layer 2 novel | Shared Libra context selection is multi-novel, but term priority and false positives remain novel-specific |
| Bracket/system-message density | Layer 1 language + Layer 2 novel | English-source system/UI patterns need language rules, while IRS has story-specific Constellation/system conventions |
| Repeated-character risk | Layer 0 multi-novel | Shared guardrails should catch runaway repeated characters regardless of novel |
| Embedded CJK/Hangul in English source | Layer 1 language + Layer 2 IRS | English-to-Thai playbook needs handling, but name policy belongs to IRS |
| DSE title sidecar requirement | Layer 1 Chinese + Layer 2 DSE | Chinese named titles need translation sidecars; DSE has existing title policy |
| Footnote/author-note heuristic | Layer 3 run-local until refined | Current signal may false-positive, especially on DSE Chinese text, so it should guide inspection before promotion |

## 5. ปัญหา อุปสรรค และการแก้ไข

1. What happened: inline analyzer regex ล้ม 3 ครั้งเพราะ Unicode literal บางตัวถูก PowerShell/console แปลงเป็น `?`
   How it was resolved: เปลี่ยน regex ที่มี Unicode literal เป็น Unicode escape และลด sound-effect detector ให้พึ่ง repeated-character risk แทน
   Outcome after resolution: analyzer สร้าง JSON/Markdown report สำเร็จ

2. What happened: glossary frontmatter ใช้ `aliases` หลายรูปแบบ เช่น `[]`, inline list, และ block list
   How it was resolved: ทำ parser ให้รับทั้งสามรูปแบบในรอบ analyzer
   Outcome after resolution: โหลด approved glossary terms ได้ DSE 168, HGD 297, IRS 363

3. What happened: DSE source upstream มีมากกว่า local pool แต่รอบนี้มี local raw แค่ `ch001-ch180`
   How it was resolved: ใช้เฉพาะ verified local pool ตาม V6.34A และบันทึก limitation ไว้
   Outcome after resolution: baseline รอบนี้ถูกต้องสำหรับ verified local pool แต่ยังไม่พิสูจน์ DSE upstream beyond `ch180`

## 6. ข้อสรุปและก้าวต่อไป

ข้อสรุป: V6.34B read-only baseline is complete and shows IRS is the main stress test for the next provider-backed in-sample run.

- Source ครบ 60/60 ไม่มี missing source
- Provider calls = 0
- Production artifacts modified = false
- Risk table ชี้ว่าต้องเน้น long-source, bracket/system UI, repeated-character, and scoped glossary handling ก่อน scaling

ก้าวต่อไป:
1. Start V6.34C with a bounded in-sample wave, not all 30 chapters at once.
2. Prioritize IRS high-risk in-sample chapters (`ch009`, `ch076`, `ch086`, `ch157`, `ch183`, `ch201`, `ch252`, `ch300`, `ch338`, `ch381`) as the first stress wave.
3. Keep DSE/HGD in-sample waves separate so failures can be classified by multi-novel/language/novel layer.
