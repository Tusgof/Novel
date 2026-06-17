# HGD ch091-ch100 Glossary Gate

Date: 2026-06-17
Run ID: `hgd-ch091-ch100-v1`

## Scope

- Chapters: `ch091-ch100`
- Scan artifact: `04_Work/_batch/hgd-ch091-ch100-v1/glossary_scan.json`
- Candidate count: 21
- Translation not started before this decision.

## Approved Terms

New notes:

- `Rowan` -> `โรวัน`
- `Melas Rank` -> `ระดับเมลาส`
- `Melas-Ranked Anomalies` -> alias/context rendering under `Melas Rank`; use `อโนมาลีระดับเมลาส`
- `Surrounding Zone` -> `เขตโดยรอบ`
- `Jason Fingler` -> `เจสัน ฟิงเลอร์`
- `The Bureau` / `Bureau` -> `สำนักงาน`
- `Jay` -> `เจย์`
- `Rosanne` -> `โรซานน์`
- `The Anomaly` / `Anomaly` -> `อโนมาลี`
- `Tik Tik` -> `ติ๊ก ติ๊ก`
- `Bonus Quest Activated` -> `เควสต์โบนัสเริ่มทำงาน`
- `Difficulty` -> `ระดับความยาก`
- `Reward` -> `รางวัล`
- `Twisted Exploration Squad` -> `หน่วยสำรวจชายบิดเบี้ยว`

Updated existing notes:

- `Thrall Class Anomalous Entity`: repaired corrupted Thai value from question marks to `เอนทิตีผิดปกติคลาสบริวาร`; added `Thrall Class` alias.
- `Twisted Man`: added `The Twisted Man` alias.

## Rejected / No New Note

- `Agent`: generic role; existing `Field Agent` covers the formal title.
- `Twisted`: descriptive adjective; covered by `Twisted Man` where entity-specific.
- `Both Kyle`: scan fragment/noise.
- `Seth Thorn Seeing`: scan fragment/noise and likely line-break contamination around `Seth Thorne`.

## Guardrail Notes

- The repaired `Thrall Class Anomalous Entity` note was necessary because an approved glossary value containing `????????` would directly damage production translations.
- Batch approval should now be committed with `approve-terms --batch`, not by repeated per-chapter manual ledger edits.
