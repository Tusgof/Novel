# Glossary Approval Decisions - dse-ch196-ch200-v1

## Scope

- Novel: Deep Sea Embers
- Run ID: `dse-ch196-ch200-v1`
- Chapters: `ch196-ch200`
- Candidate count: `13`

## Approved Terms

| Chinese | Thai | Category | First Seen |
| --- | --- | --- | --- |
| `神圣的提灯` | `ตะเกียงศักดิ์สิทธิ์` | item | `ch196-block-001` |
| `子嗣残渣` | `เศษซากทายาท` | entity | `ch196-block-001` |
| `黑伞` | `ร่มดำ` | item | `ch196-block-002` |
| `分裂体` | `ร่างแยก` | entity | `ch196-block-003` |
| `共生者` | `ผู้ร่วมชีพ` | entity | `ch197-block-002` |

## Rejected Terms

| Chinese | Reason |
| --- | --- |
| `太阳的异端` | Phrase variant already covered by approved `太阳异端` -> `พวกนอกรีตสุริยะ`. |
| `圣职者` | Generic clergy term; no stable named title evidence in this batch. |
| `贫民窟` | Generic location noun. |
| `巨人` | Generic noun; specific `星光巨人` is already approved. |
| `噪声` | Generic symptom/description term. |
| `石子` | Generic object; specific `石子手链` is already approved. |
| `天气` | Generic weather noun. |
| `左轮手` | Fragment/noisy substring from `左轮手枪`. |

## Guardrails

- No translation/refinement/QA/formatting stages were run during approval.
- Existing approved terms were preferred over approving phrase variants.
- Runtime stage names and provider routing remain unchanged.

## Next Step

Run:

```powershell
novel-pipeline --config ".system/config.yaml" approve-terms --run-id dse-ch196-ch200-v1 --batch --decision-report "07_Reports/glossary_approval_decisions_dse-ch196-ch200-v1.md"
```
