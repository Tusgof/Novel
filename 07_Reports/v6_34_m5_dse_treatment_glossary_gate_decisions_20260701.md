# V6.34 M5 DSE Treatment Glossary Gate Decisions

Date: 2026-07-01
Run ID: `v6-34-m5-dse-treatment-v1`
Experiment vault: `Deep Sea Embers/04_Work/_experiments/v6_34_m5_dse_treatment_v1`

## Summary

Fresh DSE treatment scan-only gate completed after rebuilding the experiment vault from current production raw source and passing source parity.

- Chapters: `ch017`, `ch034`, `ch048`, `ch060`, `ch081`, `ch094`, `ch114`, `ch142`, `ch161`, `ch168`
- Candidates found: 30
- Approved new glossary notes: 0
- Rejected/held candidates: 30
- Production glossary changes: none
- Production output changes: none
- MoonRead changes: none

## Decision Policy

For V6.34 M5 treatment measurement, the purpose is to measure the selected treatment set, not tune DSE glossary with newly scanned terms mid-treatment. Therefore all newly scanned DSE candidates are held/rejected for this experiment-local gate unless they are clear proper nouns or unequivocal recurring lore terms that would otherwise invalidate the measurement.

No candidate met that strict threshold in this scan.

## Rejected / Held Candidates

| Term | Reason |
|---|---|
| `幽灵船` | generic/descriptive; existing approved terms already cover key ship/entity concepts |
| `船长` | generic role |
| `罗盘` | generic object |
| `毛笔` | noisy/misidentified; context is likely `羽毛笔` |
| `邓肯船长` | character-title phrase; covered by `邓肯` and role wording |
| `船员` | generic role |
| `幽灵船长` | descriptive/title phrase, not a stable named title in this gate |
| `光线` | generic |
| `影子` | generic |
| `光网` | descriptive image |
| `星河` | generic/poetic image |
| `铁链` | generic object |
| `鸽子` | generic unless later proven named/signature entity |
| `船长室` | generic location |
| `幽灵` | generic supernatural noun |
| `城邦` | generic polity/location type |
| `高兴` | noise/common adjective |
| `圣像` | generic religious object |
| `破碎的船` | descriptive title phrase, not approved as a stable glossary term |
| `垠海` | fragment/noisy substring risk |
| `长剑` | generic object |
| `一扇门` | generic phrase |
| `深海` | generic and overlaps existing deeper DSE sea terminology |
| `常识` | generic concept |
| `大火` | generic event |
| `印记` | generic mark/symbol |
| `博物馆` | generic location type |
| `许多` | noise/common word |
| `老妇人` | generic person descriptor |
| `女神` | generic title/entity type |

## Approval Records

`approve-terms --batch` appended `glossary_approved` records for the 10 batch chapters using this decision report. It did not create glossary notes.
