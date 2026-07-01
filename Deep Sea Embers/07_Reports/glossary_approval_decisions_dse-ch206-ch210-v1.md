# Glossary Approval Decisions - dse-ch206-ch210-v1

## Scope

- Novel: Deep Sea Embers
- Run ID: `dse-ch206-ch210-v1`
- Chapters: `ch206-ch210`
- Candidate count: `26`

## Approved Terms

| Chinese | Thai | Category | First Seen |
| --- | --- | --- | --- |
| `葛莫娜` | `เกโมนา` | character | `ch206-block-002` |
| `艾登` | `ไอเดน` | character | `ch206-block-003` |
| `觅血罗盘` | `เข็มทิศตามโลหิต` | item | `ch206-block-003` |
| `神圣蒸汽` | `ไอน้ำศักดิ์สิทธิ์` | phenomenon | `ch206-block-001` |
| `舰载教堂` | `โบสถ์ประจำเรือรบ` | location | `ch206-block-002` |
| `灵体烈焰` | `เปลวเพลิงร่างวิญญาณ` | phenomenon | `ch207-block-001` |

## Rejected Terms

| Chinese | Reason |
| --- | --- |
| `钢铁战舰` | Descriptive noun phrase; not a stable named term. |
| `战舰` | Generic noun. |
| `不死人水兵` | Descriptive role phrase; translate contextually. |
| `不死人牧师` | Descriptive role phrase; translate contextually. |
| `女神圣像` | Generic object phrase; existing `风暴女神` covers the deity. |
| `教堂锅炉` | Generic device phrase; translate contextually. |
| `神圣蒸汽管道` | Composed phrase using approved `神圣蒸汽`; no separate glossary entry needed. |
| `失乡号事件` | Composed event phrase using approved `失乡号`; no separate glossary entry needed. |
| `油脂与蒸汽具在` | Noisy/misidentified phrase. |
| `雾号` | Fragment of approved `海雾号`. |
| `海雾` | Fragment/short surface of approved `海雾号`; do not create overlapping term. |
| `活死人` | Generic supernatural noun; translate contextually unless it becomes a formal faction. |
| `舵手` | Generic role noun. |
| `幻影` | Generic noun. |
| `钟楼` | Generic location noun. |
| `骂人` | Generic verb phrase. |
| `火海` | Generic imagery noun. |
| `敌人` | Generic noun. |
| `整个城` | Fragment/noisy substring. |
| `高阶` | Generic modifier/fragment. |

## Guardrails

- No translation/refinement/QA/formatting stages were run during approval.
- Existing approved terms were preferred over approving overlapping fragments.
- `海雾号`, `风暴女神`, and `失乡号` remain the source-of-truth entries for related phrases.
- Runtime stage names and provider routing remain unchanged.

## Next Step

Run:

```powershell
novel-pipeline --config ".system/config.yaml" approve-terms --run-id dse-ch206-ch210-v1 --batch --decision-report "07_Reports/glossary_approval_decisions_dse-ch206-ch210-v1.md"
```
