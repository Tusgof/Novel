# V6.34 M5 DSE Treatment V2 Glossary Gate Decisions

Date: 2026-07-01
Run ID: `v6-34-m5-dse-treatment-v2`
Experiment vault: `Deep Sea Embers/04_Work/_experiments/v6_34_m5_dse_treatment_v2`

## Summary

DSE treatment V2 was rebuilt with current production `03_Raw/manifest.json`, current production raw chapter files, and current production title sidecars. Source parity passed before and after scan-only.

- Chapters: `ch017`, `ch034`, `ch048`, `ch060`, `ch081`, `ch094`, `ch114`, `ch142`, `ch161`, `ch168`
- Candidates found: 30
- Approved new glossary notes: 0
- Rejected/held candidates: 30
- Production glossary changes: none
- Production output changes: none
- MoonRead changes: none

## Decision Policy

For V6.34 M5 treatment measurement, do not tune DSE glossary mid-treatment unless a candidate is a clear proper noun or an unequivocal recurring lore term whose absence would invalidate the experiment. This scan did not produce a candidate that met that strict threshold.

## Rejected / Held Candidates

| Term | Reason |
|---|---|
| `许多` | noise/common word |
| `睁开眼` | generic phrase |
| `阴影` | generic |
| `石头` | generic object |
| `尸体` | generic horror/body term |
| `幽灵船` | descriptive/generic; existing ship/entity glossary covers key named terms |
| `山羊大副` | descriptive title phrase; existing character/role context is sufficient for this experiment gate |
| `灵体火焰` | descriptive phenomenon; related approved terms already cover spirit/fire concepts |
| `投射状态` | descriptive state, not stable proper noun |
| `一波` | noise/common phrase |
| `周围` | noise/common word |
| `鱼线` | generic object |
| `幽绿色火焰` | descriptive color/fire phrase |
| `深海` | generic and overlaps existing DSE sea terminology |
| `女神` | generic title/entity type |
| `木门` | generic object |
| `好像` | noise/common word |
| `击声` | fragment/noisy sound term |
| `身影` | generic |
| `场大火` | fragment of `一场大火` |
| `有人` | noise/common word |
| `大火` | generic event |
| `大人` | generic address/title |
| `怪梦` | descriptive/generic |
| `鸽子` | generic unless later proven named/signature entity |
| `方面` | noise/common word |
| `火海` | generic/descriptive |
| `博物馆` | generic location type |
| `噩梦` | generic concept |
| `普通人` | generic descriptor |

## Approval Records

`approve-terms --batch` appended `glossary_approved` records for the 10 batch chapters using this decision report. It did not create glossary notes.
