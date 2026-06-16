# V6.13 Glossary Queue Review - 2026-06-16

Purpose: review the 46 visible untracked glossary notes without staging or committing the notes themselves.

No provider calls were made. No ledger, source, output, MoonRead, provider config, or pipeline runtime files were modified.

## Summary

| check | result |
| --- | --- |
| untracked glossary notes | 46 |
| tracked glossary notes | 67 |
| status distribution | approved: 46 |
| category distribution | character: 3, entity: 4, item: 7, location: 11, organization: 1, phenomenon: 10, term: 2, title: 8 |
| missing required fields | 0 |
| duplicate original terms inside untracked queue | 0 |
| duplicate Thai terms inside untracked queue | 0 |
| original-term overlaps with tracked glossary | 0 |
| Thai-term overlaps with tracked glossary | 1 |

## Findings

- All 46 untracked glossary notes are `status: approved`.
- All 46 notes have `original_term`, `thai_term`, `status`, and `category`.
- No duplicate `original_term` or `thai_term` was found inside the untracked queue itself.
- No untracked note has the same `original_term` as a tracked glossary note.
- One Thai-term overlap with the tracked glossary needs human/Codex review before committing glossary notes:
  - `01_Glossary/真实的太阳神.md`: `真实的太阳神` -> `สุริยเทพที่แท้จริง` overlaps tracked `01_Glossary/实太阳神.md`: `实太阳神` -> `สุริยเทพที่แท้จริง`

## Recommendation

- Do not delete or hide these notes.
- Do not bulk commit all 46 notes in the same commit as code/runtime changes.
- Recommended next action is a dedicated glossary commit after resolving the one alias/overlap question: whether `真实的太阳神` should remain a separate approved note, become an alias of `实太阳神`, or be moved to a variant/see-also field if the glossary schema supports it.
- If keeping both terms, document that they intentionally share the Thai rendering `สุริยเทพที่แท้จริง`.

## Untracked Glossary Notes

| path | original_term | thai_term | status | category | first seen | approved_by |
| --- | --- | --- | --- | --- | --- | --- |
| `01_Glossary/亚空间.md` | `亚空间` | `อวกาศย่อย` | `approved` | `location` | `ch007 ch007-block-002` | `codex_retranslate_glossary_gate` |
| `01_Glossary/亡灵法师.md` | `亡灵法师` | `เนโครแมนเซอร์` | `approved` | `title` | `ch021 ch021-block-003` | `codex_retranslate_glossary_gate` |
| `01_Glossary/人偶小姐.md` | `人偶小姐` | `คุณหนูตุ๊กตา` | `approved` | `title` | `ch022 ch022-block-001` | `codex_retranslate_glossary_gate` |
| `01_Glossary/人偶爱丽丝.md` | `人偶爱丽丝` | `ตุ๊กตาอลิซ` | `approved` | `character` | `ch021 ch021-block-005` | `codex_retranslate_glossary_gate` |
| `01_Glossary/哥特人偶.md` | `哥特人偶` | `ตุ๊กตาโกธิค` | `approved` | `entity` | `ch011 ch011-block-001` | `codex_retranslate_glossary_gate` |
| `01_Glossary/图腾柱.md` | `图腾柱` | `เสาโทเท็ม` | `approved` | `item` | `ch021 ch021-block-002` | `codex_retranslate_glossary_gate` |
| `01_Glossary/圣徽道标.md` | `圣徽道标` | `เครื่องหมายนำทางตราศักดิ์สิทธิ์` | `approved` | `item` | `ch006 ch006-block-003` | `codex_retranslate_glossary_gate` |
| `01_Glossary/地球.md` | `地球` | `โลก` | `approved` | `location` | `ch024 ch024-block-004` | `codex_retranslate_glossary_gate` |
| `01_Glossary/基石.md` | `基石` | `ปฐมฐาน` | `approved` | `term` | `ch049 ch049-block-001` | `codex_ch001_ch050_v2_glossary_gate` |
| `01_Glossary/复生亡魂.md` | `复生亡魂` | `วิญญาณคืนชีพ` | `approved` | `entity` | `ch021 ch021-block-003` | `codex_retranslate_glossary_gate` |
| `01_Glossary/太阳神.md` | `太阳神` | `เทพแห่งดวงอาทิตย์` | `approved` | `title` | `ch021 ch021-block-003` | `codex_retranslate_glossary_gate` |
| `01_Glossary/失乡者.md` | `失乡者` | `ผู้ไร้บ้าน` | `approved` | `title` | `ch016 ch016-block-002` | `codex_retranslate_glossary_gate` |
| `01_Glossary/失乡者之门.md` | `失乡者之门` | `ประตูแห่งผู้ไร้บ้าน` | `approved` | `item` | `ch022 ch022-block-001` | `codex_retranslate_glossary_gate` |
| `01_Glossary/封印间.md` | `封印间` | `ห้องผนึก` | `approved` | `location` | `ch006 ch006-block-004` | `codex_retranslate_glossary_gate` |
| `01_Glossary/幽灵烈焰.md` | `幽灵烈焰` | `เปลวเพลิงวิญญาณ` | `approved` | `phenomenon` | `ch011 ch011-block-003` | `codex_retranslate_glossary_gate` |
| `01_Glossary/幽邃深度.md` | `幽邃深度` | `ระดับลึกอันเร้นลับ` | `approved` | `location` | `ch006 ch006-block-002` | `codex_retranslate_glossary_gate` |
| `01_Glossary/异常物品.md` | `异常物品` | `สิ่งของผิดปกติ` | `approved` | `item` | `ch016 ch016-block-004` | `codex_retranslate_glossary_gate` |
| `01_Glossary/异象灾害.md` | `异象灾害` | `ภัยพิบัติจากปรากฏการณ์ผิดปกติ` | `approved` | `phenomenon` | `ch006 ch006-block-003` | `codex_retranslate_glossary_gate` |
| `01_Glossary/探险家协会.md` | `探险家协会` | `สมาคมนักสำรวจ` | `approved` | `organization` | `ch006 ch006-block-003` | `codex_retranslate_glossary_gate` |
| `01_Glossary/普兰德.md` | `普兰德` | `ปรานด์` | `approved` | `location` | `ch006 ch006-block-002` | `codex_retranslate_glossary_gate` |
| `01_Glossary/普兰德城邦.md` | `普兰德城邦` | `นครรัฐปรานด์` | `approved` | `location` | `ch025 ch025-block-003` | `codex_retranslate_glossary_gate` |
| `01_Glossary/木雕山羊头.md` | `木雕山羊头` | `หัวแพะแกะสลักไม้` | `approved` | `entity` | `ch011 ch011-block-005` | `codex_retranslate_glossary_gate` |
| `01_Glossary/灵体之帆.md` | `灵体之帆` | `ใบเรือร่างวิญญาณ` | `approved` | `item` | `ch007 ch007-block-001` | `codex_retranslate_glossary_gate` |
| `01_Glossary/灵体之火.md` | `灵体之火` | `เปลวไฟแห่งร่างวิญญาณ` | `approved` | `phenomenon` | `ch016 ch016-block-002` | `codex_retranslate_glossary_gate` |
| `01_Glossary/灵体形态.md` | `灵体形态` | `สภาพร่างวิญญาณ` | `approved` | `phenomenon` | `ch011 ch011-block-005` | `codex_retranslate_glossary_gate` |
| `01_Glossary/灵界海域.md` | `灵界海域` | `น่านน้ำมิติวิญญาณ` | `approved` | `location` | `ch007 ch007-block-002` | `codex_retranslate_glossary_gate` |
| `01_Glossary/灵界表层.md` | `灵界表层` | `ชั้นผิวของมิติวิญญาณ` | `approved` | `location` | `ch006 ch006-block-002` | `codex_retranslate_glossary_gate` |
| `01_Glossary/灵界边缘.md` | `灵界边缘` | `ขอบของมิติวิญญาณ` | `approved` | `location` | `ch007 ch007-block-002` | `codex_retranslate_glossary_gate` |
| `01_Glossary/灵魂投射.md` | `灵魂投射` | `การฉายจิตวิญญาณ` | `approved` | `phenomenon` | `ch021 ch021-block-001` | `codex_retranslate_glossary_gate` |
| `01_Glossary/灵魂穿梭.md` | `灵魂穿梭` | `การเดินทางข้ามผ่านของวิญญาณ` | `approved` | `phenomenon` | `ch024 ch024-block-004` | `codex_retranslate_glossary_gate` |
| `01_Glossary/爱丽丝.md` | `爱丽丝` | `อลิซ` | `approved` | `character` | `ch011 ch011-block-006` | `codex_retranslate_glossary_gate` |
| `01_Glossary/现实边境.md` | `现实边境` | `ชายขอบแห่งความจริง` | `approved` | `location` | `ch006 ch006-block-001` | `codex_retranslate_glossary_gate` |
| `01_Glossary/真实的太阳神.md` | `真实的太阳神` | `สุริยเทพที่แท้จริง` | `approved` | `title` | `ch021 ch021-block-001` | `codex_retranslate_glossary_gate` |
| `01_Glossary/真菌岛.md` | `真菌岛` | `เกาะเชื้อรา` | `approved` | `location` | `ch046 ch046-block-004` | `codex_ch001_ch050_v2_glossary_gate` |
| `01_Glossary/精灵.md` | `精灵` | `เอลฟ์` | `approved` | `term` | `ch045 ch045-block-005` | `codex_ch001_ch050_v2_glossary_gate` |
| `01_Glossary/精神投射.md` | `精神投射` | `การฉายจิต` | `approved` | `phenomenon` | `ch024 ch024-block-004` | `codex_retranslate_glossary_gate` |
| `01_Glossary/绿火.md` | `绿火` | `เปลวไฟสีเขียว` | `approved` | `phenomenon` | `ch007 ch007-block-001` | `codex_retranslate_glossary_gate` |
| `01_Glossary/艾伊.md` | `艾伊` | `ไออี` | `approved` | `character` | `ch025 ch025-block-001` | `codex_retranslate_glossary_gate` |
| `01_Glossary/诅咒人偶.md` | `诅咒人偶` | `ตุ๊กตาต้องคำสาป` | `approved` | `entity` | `ch011 ch011-block-001` | `codex_retranslate_glossary_gate` |
| `01_Glossary/超凡异象.md` | `超凡异象` | `ปรากฏการณ์เหนือธรรมชาติ` | `approved` | `phenomenon` | `ch012 ch012-block-001` | `codex_retranslate_glossary_gate` |
| `01_Glossary/面具神官.md` | `面具神官` | `นักบวชแห่งเทพหน้ากาก` | `approved` | `title` | `ch021 ch021-block-001` | `codex_retranslate_glossary_gate` |
| `01_Glossary/风暴女神.md` | `风暴女神` | `เทพีแห่งพายุ` | `approved` | `title` | `ch040 ch040-block-002` | `codex_ch001_ch050_v2_glossary_gate` |
| `01_Glossary/黄铜罗盘.md` | `黄铜罗盘` | `เข็มทิศทองเหลือง` | `approved` | `item` | `ch016 ch016-block-002` | `codex_retranslate_glossary_gate` |
| `01_Glossary/黑曜石小刀.md` | `黑曜石小刀` | `มีดสั้นหินออบซิเดียน` | `approved` | `item` | `ch021 ch021-block-002` | `codex_retranslate_glossary_gate` |
| `01_Glossary/黑炎.md` | `黑炎` | `เปลวไฟสีดำ` | `approved` | `phenomenon` | `ch021 ch021-block-004` | `codex_retranslate_glossary_gate` |
| `01_Glossary/黑袍神官.md` | `黑袍神官` | `นักบวชชุดคลุมดำ` | `approved` | `title` | `ch025 ch025-block-003` | `codex_retranslate_glossary_gate` |

## Stop Rule

Glossary notes should remain untracked until a dedicated glossary decision is made. This report is evidence only; it is not approval to commit the glossary queue.
