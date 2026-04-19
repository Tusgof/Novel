# MASTER_PLAN: ระบบแปลนิยายแบบ Local Pipeline + Skill-Orchestrated Runtime

> Status: Current canonical master plan
>
> ไฟล์นี้เป็นแผนหลักฉบับรวม

## Summary
สร้างระบบแปลนิยายแบบ local-first ที่ใช้ Python เป็น execution engine ของ pipeline และใช้ skills เป็น orchestration/policy layer สำหรับการใช้งานผ่าน Codex

หลักการที่ล็อกแล้ว:
- `1 นิยาย = 1 Obsidian vault`
- รองรับ `ภาษาจีนเป็นหลัก` และเผื่ออังกฤษเป็นลำดับถัดไป
- runtime ใช้ CLI non-interactive (`gemini`, `claude`, `qwen`, `codex`)
- workflow หลักคือ `fetch -> pre-scan glossary -> human approve -> literal -> refine -> QA -> format -> save`
- human gate หลักอยู่ที่ `glossary approval`
- batch run ใช้ `pre-scan glossary ก่อน แล้วค่อย bulk run`
- glossary retrieval ใช้ `ดึงเฉพาะศัพท์ที่ match กับ block`
- QA ใช้ `hybrid rules + AI judge`
- ถ้า QA ไม่ผ่าน ต้อง `ส่งกลับ refiner พร้อม feedback`
- สถาปัตยกรรมรวมใช้แนว `runtime in Python, policy in skills`

---

## 1. Runtime Pipeline

### 1.1 Pipeline stages
ระบบแบ่งเป็น 7 stage และทุก stage ต้องมี input/output contract ชัดเจน

1. `Fetcher`
- รับต้นฉบับจาก:
  - paste text
  - local file
  - website adapter
- ถ้าเป็นเว็บ ให้ใช้ `adapter per source site`
- output มาตรฐาน:
  - novel id
  - chapter id / title
  - source url
  - source language
  - raw text
  - fetched timestamp

2. `Glossary Pre-Scan`
- ทำงานก่อนเริ่มแปลทั้ง batch
- สแกนทุก chapter ใน batch เพื่อหา candidate terms
- ใช้สองชั้น:
  - heuristic/regex
  - AI-assisted term extraction
- รวมคำใหม่ทั้ง batch แล้ว deduplicate ก่อนถามผู้ใช้
- lookup glossary จาก vault โดยใช้ `คำต้นฉบับ` เป็น primary key

3. `Glossary Approval`
- ถ้าพบคำใหม่ ให้สร้างรายการรออนุมัติ
- แต่ละคำต้องแสดงใน terminal พร้อม:
  - `context`
  - `category`
  - `short rationale`
  - ตัวเลือกคำแปล 3 แบบ
- ผู้ใช้เลือกผ่าน `input()`
- เมื่อเลือกแล้ว ระบบสร้าง glossary note ทันที และอัปเดตฐานศัพท์ก่อนเริ่ม translate
- ถ้าคำใด approve แล้ว ห้ามถามซ้ำใน run เดิมหรือ run ถัดไป เว้นแต่มีการเปลี่ยนสถานะเอง

4. `Literal Translation Agent`
- ใช้ `Gemini` เป็น default
- แปลแบบ sentence-by-sentence
- กฎแข็ง:
  - ห้าม omission
  - ห้าม addition
  - ห้าม embellishment
  - ห้ามทำให้เป็นสำนวนไทยลื่นเกินต้นฉบับ
- output ต้องเก็บคู่:
  - source sentence
  - literal Thai sentence
- literal draft ถือเป็น `source of truth` ของงานแปลหลังจากต้นฉบับ

5. `Refiner Agent`
- ใช้ `Claude` เป็น default
- รับ:
  - literal draft
  - block context
  - glossary subset
  - style profile ของเรื่อง
- หน้าที่:
  - reword / restructure ให้อ่านลื่นขึ้น
  - ปรับจังหวะภาษาและสรรพนาม
  - คง fact, plot intent, named entities, relationships ตาม literal draft
- ห้ามเปลี่ยนสาระสำคัญ
- ถ้า QA ไม่ผ่าน ตัวนี้คือ stage ที่ต้องรับ feedback แล้วย้อนมาแก้ใหม่

6. `QA Gate`
- เป็น mandatory stage หลัง refine ก่อน format
- ใช้ `Hybrid rules + AI judge`
- ตรวจ 2 ระดับ:
  - `line-by-line`: เช็กว่า refined text ยังสื่อสารตรงกับ literal/source ไม่ตกหล่น ไม่เพี้ยน
  - `paragraph-by-paragraph`: เช็กว่าย่อหน้า การรวม/แยก การไหลของข้อความ ยังรักษาความหมายเดิม
- rule-based checks ขั้นต่ำ:
  - missing/empty output
  - glossary consistency
  - proper-name drift
  - block/paragraph structure mismatch
- AI judge checks:
  - semantic fidelity
  - omission/addition suspicion
  - paragraph intent preservation
- ถ้า QA fail:
  - mark block เป็น failed
  - สร้าง feedback report
  - ส่ง `source block + literal draft + failed refined draft + feedback` กลับไปให้ refiner แก้ใหม่
- ไม่ปล่อย block นั้นไป stage ถัดไปจนกว่าจะผ่านหรือเกิน retry limit

7. `Formatter`
- ทำงานหลัง QA ผ่านแล้วเท่านั้น
- จัด:
  - paragraph spacing
  - quote formatting
  - line breaks
  - readability layout
- ไม่แตะ meaning
- output เป็น markdown note พร้อม metadata chapter/block

### 1.2 Batch orchestration
ระบบระยะยาวต้องรองรับการทำงานเป็นช่วง ไม่ใช่ chapter เดียวต่อครั้ง

default orchestration:
- ใช้ `Pre-scan then bulk run`
- หนึ่ง batch = `1 arc หรือช่วงตอน`
- default batch size = `10-20 chapters`

flow ของ batch:
1. fetch chapters ในช่วงที่กำหนด
2. pre-scan candidate terms ทั้ง batch
3. deduplicate terms
4. ให้ผู้ใช้ approve glossary รอบเดียว
5. lock glossary snapshot ของ batch
6. รัน `literal -> refine -> QA -> format` ตาม chapter/block
7. บันทึก output และ run logs

policy ของ batch:
- chapter ต้องรันตามลำดับ
- block ภายใน chapter ต้อง preserve order
- ถ้า block ใด QA fail:
  - หยุด chapter นั้นก่อน
  - ส่งกลับ refiner ตาม retry policy
  - ไม่ข้าม silently
- chapter ถัดไปจะไม่รันต่อจนกว่าบทปัจจุบันผ่าน หรือผู้ใช้ override policy เองในอนาคต

### 1.3 Glossary retrieval / RAG policy
ไม่ควรดึง glossary ทั้งเรื่องเข้า prompt ทุกครั้ง เพราะจะเกิด noise และเปลือง token

default retrieval policy:
- ดึง `เฉพาะศัพท์ที่ match กับ block`
- รวม:
  - exact match
  - alias match
  - related term ที่จำเป็นต่อความเข้าใจ
- ไม่ดึงศัพท์ทั้งเรื่องแบบเหมา เว้นแต่ภายหลังมี special override

retrieval flow:
1. parse block text
2. ตรวจ candidate matches กับ glossary index
3. resolve alias -> canonical term
4. เพิ่ม related entries เฉพาะที่มี dependency จริง
5. build compact glossary context สำหรับ prompt

ข้อมูลที่ส่งเข้า prompt ต่อ term:
- original term
- approved Thai term
- category/type
- short description
- alias ที่จำเป็น
- related note เฉพาะกรณีเกี่ยวข้องจริง

### 1.4 Folder structure ต่อ 1 นิยาย
โครงสร้างแนะนำ:

- `00_Templates/`
- `01_Glossary/`
- `02_Database_Views/`
- `03_Raw/`
- `04_Work/`
- `05_Output/`
- `06_Logs/`
- `.system/`

หน้าที่:
- `00_Templates`
  - template สำหรับ glossary note, chapter note, run note
- `01_Glossary`
  - 1 term = 1 note
- `02_Database_Views`
  - Dataview pages สำหรับดูศัพท์และสถานะ
- `03_Raw`
  - source chapters / blocks
- `04_Work`
  - candidate terms, literal drafts, refined drafts, QA reports, checkpoints
- `05_Output`
  - chapter markdown พร้อมอ่าน
- `06_Logs`
  - run history, provider logs, error logs
- `.system`
  - config ต่อเรื่อง, adapter config, model routing, style profile

### 1.5 Glossary schema
ใช้ `คำต้นฉบับ` เป็นชื่อไฟล์ของ glossary note

frontmatter มาตรฐาน:
- `type`
- `original_term`
- `thai_term`
- `status`
- `aliases`
- `source_language`
- `category`
- `description`
- `related`
- `novel`
- `created_at`
- `updated_at`

ค่าใช้งานหลัก:
- `status`: proposed, approved, deprecated
- `category/type`: character, location, sect, realm, item, technique
- `aliases`: รูปสะกดอื่น
- `related`: ลิงก์ `[[...]]`
- `description`: คำอธิบายย่อสำหรับมนุษย์และ AI

body ของ note:
- บทบาท/ความหมายย่อ
- ตัวอย่างบริบท 1-2 ชุด
- หมายเหตุการใช้คำแปลถ้ามี

Dataview pages ขั้นต่ำ:
- ตารางศัพท์ทั้งหมด
- ตารางศัพท์ที่ยัง proposed
- ตารางแยกตาม category

### 1.6 Chunking, state machine, resume
default block policy:
- จีน: ไม่เกิน `2,500` ตัวอักษรต่อ block
- ไทย/อังกฤษ: ไม่เกิน `4,500-5,000` คำ
- หลีกเลี่ยงการตัดกลางประโยค
- prefer ตัดตาม paragraph หรือ scene break

artifact ต่อ block:
- raw source
- glossary matches
- literal draft
- refined draft
- QA result
- formatted output
- run metadata

state machine ขั้นต่ำ:
- queued
- fetched
- glossary_scanned
- glossary_pending
- glossary_resolved
- translating
- refining
- qa_failed
- qa_passed
- formatting
- completed
- failed

resume rules:
- ถ้า approve glossary ไปแล้ว ห้ามถามซ้ำ
- ถ้า literal เสร็จแล้ว refine ล้ม ให้เริ่มจาก refine
- ถ้า QA fail แล้วมี feedback ค้างอยู่ ให้ retry จาก refiner
- ถ้า output มีอยู่แล้ว default = ไม่ overwrite เว้น `--force`

### 1.7 Provider orchestration
ใช้ `subprocess` เรียกทุก provider ใน v1-v2

ชั้น abstraction ที่ควรมี:
- `ProviderRunner`
- `PromptBuilder`
- `ResponseParser`
- `RetryPolicy`

default routing:
- `Gemini`
  - term suggestion
  - literal translation
  - long-context extraction
- `Claude`
  - refinement
  - อาจใช้เป็น AI judge สำหรับ QA บางขั้น
- `Qwen`
  - fallback utility tasks
- `Codex`
  - tooling/validation/support tasks ไม่ใช่ translator หลัก

prompt contracts แยกอย่างน้อย:
- `term_suggestion_prompt`
- `literal_translation_prompt`
- `refinement_prompt`
- `qa_judge_prompt`
- `formatting_prompt`

ทุก prompt ควรระบุ:
- role
- hard rules
- input schema
- expected output schema
- glossary context
- failure instruction
- deterministic delimiters หรือ JSON output เท่าที่ทำได้

---

## 2. Skill Architecture

### 2.1 Core principle
ใช้แนวทาง `runtime in Python, policy in skills` เพื่อให้ workflow เสถียรและบำรุงรักษาง่าย

สถาปัตยกรรมที่ล็อกแล้ว:
- ใช้ `1 main orchestrator skill`
- มี `support skills` แยกเฉพาะงานที่ต้องคุมวิธีใช้งานผ่าน Codex
- `Python engine` เป็นตัวรันจริงของ pipeline, state machine, retry, checkpoint, prompt execution
- ผู้ใช้สั่งงานผ่านหน้าคุยนี้ด้วย `high-level commands`
- Codex ใช้ skill เพื่อแปลคำสั่งระดับสูงให้เป็นการรัน workflow ที่ถูกต้อง
- จุดถามผู้ใช้มาตรฐานมีเฉพาะ `glossary approval`

### 2.2 Main skill: `novel-pipeline-orchestrator`
หน้าที่:
- ตีความคำสั่งระดับสูงของผู้ใช้ เช่น
  - รัน batch ตอน 1-10
  - fetch เรื่องนี้
  - resume งานล่าสุด
  - สแกน glossary ก่อนแปล
- ตรวจว่าต้องเรียก Python command ไหน
- enforce ลำดับงานมาตรฐาน:
  - fetch
  - pre-scan glossary
  - approve glossary
  - literal
  - refine
  - QA
  - format
  - save
- ใช้ config ต่อเรื่องเพื่อ resolve:
  - vault path
  - source adapter
  - provider routing
  - batch size
  - style profile
- บอก Codex ว่าเมื่อไรควรถามผู้ใช้ และเมื่อไรควรรันต่ออัตโนมัติ

สิ่งที่ไม่ควรอยู่ใน skill นี้:
- logic fetch รายเว็บ
- state persistence
- retry implementation
- prompt text ทั้งหมด
- parsing runtime outputs แบบละเอียด

### 2.3 Support skill: `novel-glossary-review`
หน้าที่:
- กำหนดวิธีเสนอคำศัพท์ใหม่ให้ผู้ใช้
- บังคับรูปแบบการแสดงผล:
  - original term
  - category
  - context
  - short rationale
  - 3 translation options
- กำหนดวิธีรับคำตอบจากผู้ใช้และ map ไปยัง action ที่ถูกต้อง
- ช่วย Codex ตัดสินว่าเมื่อไรควร approve, defer, หรือ flag term conflict

ไม่ควรอยู่ใน skill นี้:
- glossary indexing logic
- file write logic
- canonical term storage

### 2.4 Support skill: `novel-translation-qa`
หน้าที่:
- กำหนดวิธีอ่าน QA report
- แยกประเภท failure:
  - omission/addition risk
  - proper-name drift
  - glossary inconsistency
  - paragraph intent drift
- กำหนดว่าเมื่อไรต้องส่ง block กลับไป refiner
- ช่วย Codex สรุป QA issue ให้ผู้ใช้ถ้ามีกรณีพิเศษ

ไม่ควรอยู่ใน skill นี้:
- line alignment checker
- semantic judge execution
- retry counters
- automatic fail/pass implementation

### 2.5 Support skill: `novel-fetch-adapters`
หน้าที่:
- ช่วย Codex เลือกว่า source แบบไหนควรใช้ adapter ไหน
- บอก pattern ว่า adapter ที่ดีต้องคืนข้อมูลอะไร
- บอกข้อควรระวังของ source types:
  - table of contents pages
  - paginated chapters
  - content cleanup
  - encoding issues

ไม่ควรทำให้ skill นี้เป็นที่เก็บ scraper logic จริง
- scraper logic ต้องอยู่ใน Python modules
- skill มีหน้าที่แค่บอก Codex ว่าควรเรียก adapter ไหนและคาดหวังอะไรจากมัน

### 2.6 Boundary between skills and Python
Skill responsibilities:
- ตีความ intent ของผู้ใช้
- คุมลำดับงาน
- คุม policy
- คุมการสื่อสารกับผู้ใช้
- คุมการตัดสินใจระดับ orchestration
- ช่วย Codex ใช้เครื่องมือให้ถูกขั้น

Python responsibilities:
- run pipeline stages
- เรียก provider CLI
- load/save config
- chunking
- glossary lookup
- prompt building
- retry policy
- QA checks
- state machine
- checkpoint/resume
- logging
- output generation

Source of truth:
- `Skills`: วิธีใช้งานผ่าน Codex
- `Python engine`: วิธีรันจริง
- `Per-novel config`: ค่าเฉพาะเรื่อง
- `Versioned prompt files`: prompt templates หลัก

### 2.7 Prompt and config strategy
Prompt source of truth:
- เก็บ prompt หลักไว้เป็น `versioned prompt files in Python project`
- ครอบคลุมอย่างน้อย:
  - term suggestion
  - literal translation
  - refinement
  - QA judge
  - formatting

Skill references to prompts:
- skill ควรอ้างว่าใช้ prompt file ไหน ใช้ stage ไหน และมี policy อะไร
- ไม่ควรคัด prompt เต็มมาไว้ใน SKILL.md ยกเว้นกฎสั้น ๆ ที่จำเป็นมาก

Per-novel config:
- novel id/name
- vault root
- source language
- fetch adapter
- batch defaults
- style profile
- provider routing
- glossary rules overrides ถ้ามี

### 2.8 User interaction model
Default interaction:
- ผู้ใช้สั่งงานผ่านหน้าคุยนี้ด้วย `high-level commands`

ตัวอย่าง intent:
- รัน batch ตอน 1-10 ของเรื่องนี้
- ดึงตอนล่าสุดแล้วสแกนศัพท์ก่อน
- resume งานแปลค้าง
- สรุป QA failures ของ batch ล่าสุด

Codex behavior:
1. main orchestrator skill ตีความ intent
2. resolve config และ workflow ที่ต้องใช้
3. เรียก Python commands ที่เหมาะสม
4. ถ้ามี glossary pending ใช้ `novel-glossary-review`
5. ถ้ามี QA escalation ใช้ `novel-translation-qa`
6. รายงานสถานะและผลลัพธ์กลับผู้ใช้

Human touchpoints:
- glossary approval only

---

## 3. Public Interfaces / Types

### 3.1 Config ต่อเรื่อง
ต้องมี config กลางต่อ novel อย่างน้อย:
- novel id / name
- vault root
- source language
- fetch mode
- adapter name
- style profile
- block limits
- provider routing
- batch defaults
- output paths

### 3.2 Canonical document types
ชนิดข้อมูลหลัก:
- `ChapterSource`
- `TextBlock`
- `GlossaryEntry`
- `TermSuggestion`
- `LiteralDraft`
- `RefinedDraft`
- `QAReport`
- `RunRecord`

ข้อมูลสำคัญของ `QAReport`:
- block id
- status pass/fail
- failing checks
- semantic concerns
- glossary drift findings
- feedback text for refiner
- retry count

### 3.3 CLI commands
คำสั่งหลัก:
- `fetch`
- `scan-terms`
- `approve-terms`
- `translate-literal`
- `refine`
- `qa`
- `format`
- `run`
- `resume`
- `status`

พฤติกรรม `run`:
- รับ chapter range หรือ arc
- pre-scan glossary ก่อน
- เปิด approval flow
- bulk run ตามลำดับ
- ถ้า QA fail ให้ reroute ไป refiner ตาม retry policy
- แสดง progress ต่อ chapter/block

---

## 4. Test Plan

### 4.1 Runtime pipeline
- fetch chapter จีนจากไฟล์หรือเว็บ
- pre-scan batch ได้
- deduplicate term ถูก
- approve glossary ได้ครบ
- literal -> refine -> QA -> format -> save สำเร็จ
- output markdown อ่านได้ใน Obsidian

### 4.2 Glossary behavior
- คำที่มีอยู่แล้วต้องไม่ถูกถามซ้ำ
- alias match ได้
- term approval สร้าง note ถูก frontmatter
- terminal prompt แสดง context/category/rationale ครบ
- invalid input แล้วถามซ้ำโดย state ไม่เสีย

### 4.3 Retrieval behavior
- block ที่มีศัพท์น้อยต้องดึงเฉพาะคำที่เกี่ยวข้องจริง
- alias resolve ไป canonical entry ถูก
- related terms ไม่ถูกดึงเกินจำเป็น
- prompt size ไม่โตโดยไม่จำเป็นเมื่อ glossary โตขึ้น

### 4.4 QA behavior
- line-by-line ตรวจพบ omission/addition ได้
- paragraph-by-paragraph ตรวจพบ drift หลัง refine ได้
- proper names เพี้ยนต้อง fail
- glossary inconsistency ต้อง fail
- QA fail แล้วสร้าง feedback ส่งกลับ refiner ได้
- retry แล้วผ่านจึงไป format ต่อ

### 4.5 Resume / failure recovery
- crash หลัง glossary approval แล้ว resume ได้
- provider timeout ระหว่าง literal/refine/QA แล้ว retry ได้
- QA fail ค้างอยู่แล้ว resume กลับไป refiner ได้
- ไม่สร้าง output ซ้ำหรือถาม glossary ซ้ำ

### 4.6 Batch behavior
- batch 10-20 chapters ทำ pre-scan ได้ครบ
- glossary queue ของ batch ถูกสร้างก่อนเริ่ม translate
- chapter order ไม่สลับ
- block failure หยุด chapter ได้ถูกต้อง
- logs/report แยกตาม chapter และ block ได้

### 4.7 Skill architecture
- คำสั่งระดับสูงเรื่อง batch run ต้อง trigger orchestrator skill ถูก
- คำสั่งเกี่ยวกับคำศัพท์ใหม่ต้อง trigger glossary review skill ถูก
- คำสั่งเกี่ยวกับ QA failure ต้อง trigger QA skill ถูก
- คำสั่ง fetch source ใหม่ต้องใช้ fetch adapter guidance ถูก
- skill ไม่ต้องแบก runtime logic สำคัญ
- Python engine ทำงานได้แม้ไม่มีบทสนทนาย้อนหลัง
- prompt files แก้ version ได้โดยไม่ต้องแก้หลาย skill
- Codex แปลคำสั่งระดับสูงเป็น workflow ที่ถูกต้องได้

---

## 5. Assumptions And Defaults
- ใช้ Python เป็น orchestration/execution layer หลัก
- ใช้ `subprocess` เรียก `gemini`, `claude`, `qwen`, `codex`
- ใช้ filesystem ของ Obsidian โดยตรง ไม่ผ่าน API
- ใช้ `Dataview` เป็นปลั๊กอินสำคัญใน vault
- ใช้ `คำต้นฉบับ` เป็น primary key ของ glossary
- v1/v2 ยังเน้น markdown output ก่อน ไม่บังคับ DOCX/EPUB
- fetch เว็บไซต์ใช้ `adapter per site`
- literal draft เป็น baseline truth สำหรับ QA และ refiner
- QA เป็น mandatory ก่อน format
- QA fail ต้องย้อนกลับ refiner พร้อม feedback
- batch default = `arc ละ 10-20 chapters`
- glossary retrieval default = `match เฉพาะ block + alias + related ที่จำเป็น`
- จะสร้าง skill ใหม่เฉพาะสำหรับระบบแปลนิยายนี้ ไม่ปนกับ skill เดิมที่ใช้ทั่วไป
- prompts จะถูกเก็บแบบ versioned files ในโปรเจกต์ ไม่เก็บกระจัดกระจายใน skills
- default interaction mode คืออัตโนมัติให้มากที่สุด และถามผู้ใช้เฉพาะตอนอนุมัติ glossary
