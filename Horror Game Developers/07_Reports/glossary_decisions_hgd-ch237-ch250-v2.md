# Glossary Decisions: hgd-ch237-ch250-v2

## Scope

- Novel: Horror Game Developer
- Run ID: `hgd-ch237-ch250-v2`
- Chapters: `ch237` through `ch250`
- Source sequence guard: passed after fetch resolver repair (`ch237` source Chapter 237 through `ch250` source Chapter 250)

## Approved

| original_term | thai_term | reason |
| --- | --- | --- |
| Soran | โซแรน | Character name; keeps standalone mentions consistent with Team Leader Soran. |
| Sacred Rite | พิธีศักดิ์สิทธิ์ | Named skill/rite in gate scenario context. |
| Malovia Islands | หมู่เกาะมาโลเวีย | Named location; plural form should not drift from Malovia Island. |
| Velmoor Opera House | โรงอุปรากรเวลมัวร์ | Named location. |
| Code Violet | รหัสม่วง | Guild emergency code. |
| Code Green | รหัสเขียว | Guild emergency code. |
| Code Orange | รหัสส้ม | Guild emergency code inferred from Singular Team Code Orange context. |
| The BAU | BAU | Alias for approved BAU acronym. |

## Existing Terms Reused

- `Team Leader Soran` -> `หัวหน้ากลุ่มโซแรน`
- `Squad Leader` -> `หัวหน้ากลุ่ม`
- `The Team Leader` -> `หัวหน้าทีม`
- `VILE` -> `VILE`
- `Jester` -> `ตัวตลก`
- `Academy` is covered contextually by `Newton Academy` where relevant.
- `Anomalous-Type Gate`, `S-Ranked Gate`, and related gate terms are already covered by existing glossary entries.

## Rejected / Contextual

- Generic or noisy phrases: `Besides Sarah`, `On Loan`, `Extremely Dangerous`, `The PC`, `Possessed`, `Gates`, `The Gate`, `All Guild`, `The Codes`, `Entire Guild There`, `Meet VILE`
- Stutter/noise fragments: `S-squad Leader`, `S-quad Leader`, `S-squad L-leader`
- Title variants already covered by existing glossary: `The Squad Leader`, `Their Squad Leader`, `The BAU`
- Phrase-level candidate rejected in favor of smaller approved term: `Singular Team Code Orange`

## Guardrail Note

The first scan attempt used `hgd-ch237-ch250-v1` and fetched source Chapters 253-266 because HGD manifest ordinal IDs conflicted with website chapter numbers. That run was abandoned. Runtime artifacts from the bad run were removed, and the fetch resolver now prefers `metadata.site_chapter` for chapter ID resolution.
