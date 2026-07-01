# Glossary Approval Decisions - dse-ch201-ch205-v1

## Scope

- Novel: Deep Sea Embers
- Run ID: `dse-ch201-ch205-v1`
- Chapters: `ch201-ch205`
- Candidate count: `12`

## Approved Terms

| Chinese | Thai | Category | First Seen |
| --- | --- | --- | --- |
| `蒸汽步行机` | `เครื่องจักรเดินไอน้ำ` | item | `ch201-block-001` |
| `转轮机枪` | `ปืนกลหมุนหกลำกล้อง` | item | `ch201-block-001` |
| `六管机枪` | `ปืนกลหมุนหกลำกล้อง` | item | `ch201-block-002` |
| `风暴之力` | `พลังแห่งพายุ` | ability | `ch201-block-002` |
| `风暴巨剑` | `ดาบยักษ์พายุ` | item | `ch201-block-002` |
| `古董店长` | `เจ้าของร้านขายของเก่า` | title | `ch202-block-002` |

## Rejected Terms

| Chinese | Reason |
| --- | --- |
| `毁于大火` | Descriptive phrase, not a stable term. |
| `随手` | Generic adverbial phrase. |
| `巨剑` | Generic weapon noun; only specific `风暴巨剑` is approved. |
| `城邦审判官` | Phrase variant using existing `审判官`; no new term needed. |
| `些火` | Fragment/noisy substring from `那些火焰`. |
| `老人` | Generic noun. |

## Guardrails

- No translation/refinement/QA/formatting stages were run during approval.
- Existing approved terms were preferred over approving phrase variants.
- Runtime stage names and provider routing remain unchanged.

## Next Step

Run:

```powershell
novel-pipeline --config ".system/config.yaml" approve-terms --run-id dse-ch201-ch205-v1 --batch --decision-report "07_Reports/glossary_approval_decisions_dse-ch201-ch205-v1.md"
```
