# Glossary Approval Decisions - dse-ch191-ch195-v1

## Scope

- Novel: Deep Sea Embers
- Run ID: `dse-ch191-ch195-v1`
- Chapters: `ch191-ch195`
- Candidate count: `14`

## Approved Terms

| Chinese | Thai | Category | First Seen |
| --- | --- | --- | --- |
| `蠕变日轮` | `ดวงตะวันคลานคืบ` | title | `ch191-block-002` |
| `圣徒` | `นักบุญ` | title | `ch191-block-004` |
| `断头台` | `กิโยติน` | ability | `ch191-block-004` |
| `湮灭教徒` | `สาวกแห่งการดับสูญ` | group | `ch192-block-002` |
| `传火` | `การสืบไฟ` | term | `ch194-block-005` |

## Rejected Terms

| Chinese | Reason |
| --- | --- |
| `终末` | Generic apocalyptic word; already covered contextually by approved faction/title terms. |
| `轮回` | Generic concept; no stable lore-name evidence in this batch. |
| `常识` | Generic common noun. |
| `通人` | Fragment/noisy substring from `普通人`. |
| `生气` | Generic verb/adjective phrase. |
| `案馆` | Fragment/noisy substring from `档案馆`. |
| `年神` | Fragment/noisy substring around `中年神甫`. |
| `桌子` | Generic object. |
| `铃声` | Generic sound/object term. |

## Guardrails

- No translation/refinement/QA/formatting stages were run during approval.
- No terms outside this decision report were approved.
- Runtime stage names and provider routing remain unchanged.

## Next Step

Run:

```powershell
novel-pipeline --config ".system/config.yaml" approve-terms --run-id dse-ch191-ch195-v1 --batch --decision-report "07_Reports/glossary_approval_decisions_dse-ch191-ch195-v1.md"
```
