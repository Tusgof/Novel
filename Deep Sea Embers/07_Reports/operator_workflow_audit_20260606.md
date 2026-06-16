# Operator Workflow Audit - 2026-06-06

## Summary
- milestone: V6.4 Operator Workflow Audit And Control Window Rebuild
- overall_status: action_required
- audit_scope: operator window workflow, visible controls, backend action mapping, and rebuild plan
- live_translation_or_provider_calls: none
- state_changing_pipeline_actions: none
- evidence_collected:
  - `novel-pipeline --config ".system/config.yaml" preflight`
  - served operator HTML from `http://127.0.0.1:8776/`
  - operator bootstrap snapshot from `http://127.0.0.1:8776/api/bootstrap`
  - read-only glossary queue API
  - read-only inspect-block API
  - rejected invalid `run-batch` payload against `/api/action`

## Audit Verdict
The backend control surface is present, but the current operator window is not yet suitable as the primary UI for a normal user. It exposes implementation details, requires too much prior knowledge, and makes several navigation controls look like execution controls. The next work should be a task-first rebuild, not more panel shuffling.

## Current Runtime Evidence
| check | result | evidence |
| --- | --- | --- |
| preflight | ready | providers/config/git/research readiness all ready |
| default run loaded by API | ok | `/api/bootstrap` returns `batch-ch019-ch023-v1` |
| current run state | complete | `26/26` blocks complete, current failed blocks none |
| read-only glossary queue | ok | `/api/glossary-queue?run_id=batch-ch019-ch023-v1` returns 200 |
| read-only block inspection | ok | `/api/inspect-block?...ch019-block-001` returns 200 |
| invalid state action guard | ok | empty `run-batch` payload returns 400 |
| live provider use during audit | none | no translation/refinement/QA/formatting command run |

## Workflow Audit
| workflow | current user experience | backend action | failure mode | target behavior |
| --- | --- | --- | --- | --- |
| Continue Deep Sea Embers from next range | User sees completed old run and must know to create `batch-ch024-ch028-v1` manually. UI does not lead with "next range needs scan first." | `run --range ... --stop-after glossary-scan`, then glossary decisions, then bounded run/resume | User can try to resume the completed old run or does not know which range/run ID to enter. | A `Continue Translation` task should show the completed current run, source boundary, recommended next range, and first required action: scan-only glossary gate. |
| Start scan-only glossary gate | Control exists as `Run Batch` with a mode selector, but user must understand `run_id`, `chapter_range`, and scan-only semantics. | `/api/action` with `action=run-batch`, `stop_after=glossary-scan` | Action is technically correct but not self-explanatory for normal users. | Show a dedicated `Start Glossary Scan` action with generated run ID suggestion and explicit chapter range validation. |
| Approve/reject glossary candidates | Workbench exists, but queue and decision flow are separated from the translation task path. | `/api/glossary-queue`, `/api/glossary-suggestion`, `/api/action glossary-decision` | User does not know whether glossary is required before translation or whether queue is already closed. | Glossary Review should show "pending / closed / committed" state and make the next required decision obvious. |
| Start bounded translation after glossary approval | Existing bounded batch/resume controls require manual field entry. | `/api/action run-batch` or `/api/action resume` | User must decide between run-batch and resume without UI guidance. | Continue Translation should choose the correct backend action from current run state and show exact command before execution. |
| Inspect and recover a failed block | Inspect and rerun exist but require user to know block ID and stage. | `/api/inspect-block`, `/api/action rerun-block` | If no current failed block exists, recovery panel is noise. If a failed block exists, UI should prefill from status. | Recovery task should appear only when needed or show "no failed block"; failed blocks should be selectable directly. |
| Generate reports | Report controls exist, but normal users do not know which report answers which question. | `/api/report` | Report buttons are labels without task context. | Reports should be grouped by question: "Is system ready?", "Is run complete?", "Are outputs clean?", "What failed?" |
| Create a new novel project | Setup controls exist in the same operator surface. | `/api/action init-novel`, `/api/action save-research-profile` | Setup competes visually with day-to-day translation work. | Project Setup should be a separate task mode with a short wizard-style flow. |

## Button And API Behavior Matrix
| visible control | current classification | endpoint/action | expected effect | audit result |
| --- | --- | --- | --- | --- |
| Current Run focus | navigation-only | client-side only | filters panels | works, but looks like a workflow action |
| Glossary focus | navigation-only | client-side only | filters panels | works, but should be visually secondary |
| Recovery focus | navigation-only | client-side only | filters panels | works, but should be visually secondary |
| Reports focus | navigation-only | client-side only | filters panels | works, but should be visually secondary |
| Setup focus | navigation-only | client-side only | filters panels | works, but should be visually secondary |
| All focus | navigation-only | client-side only | shows all panels | works, but adds visual overload |
| Load Run | read-only API | `/api/bootstrap?run_id=...` | loads selected run snapshot | should remain, but layout and default state need clarity |
| Refresh | read-only API | `/api/bootstrap` | reloads current snapshot | should remain |
| Open Batch Controls | navigation-only | client-side only | scrolls to batch panel | misleading as primary action; should not look like execution |
| Open Glossary Workbench | navigation-only | client-side only | scrolls to glossary panel | misleading as primary action; should not look like execution |
| Open Recovery Tools | navigation-only | client-side only | scrolls to recovery panel | misleading as primary action; should not look like execution |
| Open Report Controls | navigation-only | client-side only | scrolls to report panel | misleading as primary action; should not look like execution |
| Run Batch | state-changing bounded action | `/api/action run-batch` | runs scan-only or bounded batch range | backend guard works; UI asks for implementation details |
| Run Bounded Resume | state-changing bounded action | `/api/action resume` | resumes to chapter/block with manual stop | backend guard works; UI should only expose when appropriate |
| Load options | read-only/provider action risk | `/api/glossary-suggestion` | gets term suggestions | may call term suggestion provider; must be marked as model call if live |
| Approve Selected Option | state-changing glossary action | `/api/action glossary-decision` | writes glossary decision and may commit approval | keep, but require visible term/context confirmation |
| Reject Term | state-changing glossary action | `/api/action glossary-decision` | records rejection in queue decision | keep, but show consequence clearly |
| Inspect | read-only API | `/api/inspect-block` | loads block artifacts/stage state | keep, should be prefilled from failed block list |
| Use Pending Stage | form-fill helper | client-side only | fills rerun stage | useful, but should look like helper not action |
| Use QA Stage | form-fill helper | client-side only | fills rerun stage | useful, but should look like helper not action |
| Run Rerun-Block | state-changing bounded action | `/api/action rerun-block` | reruns one block from one stage | keep with exact command preview and confirmation |
| report buttons | read/write report artifact | `/api/report` | regenerates report file | safe but mutates tracked report artifact; label as report refresh |
| Init Novel Project | setup action | `/api/action init-novel` | creates new project scaffold | should move into setup wizard |
| Save Research Profile | setup/config action | `/api/action save-research-profile` | writes `RESEARCH_PROFILE.yaml` | should remain in setup/research task with validation summary |

## Findings
| id | severity | ease | importance | score | finding | recommended action |
| --- | --- | --- | --- | --- | --- | --- |
| UX-001 | high | 1 | 2 | 3 | The dashboard is panel-first, not task-first. Users must translate concepts like "run-batch", "resume", and "glossary-scan" into the next action. | Rebuild around task views: Continue Translation, Glossary Review, Recover Block, Reports, Project Setup. |
| UX-002 | high | 2 | 2 | 4 | Navigation controls look like action buttons. Primary Actions are especially misleading because they do not run anything. | Demote navigation to tabs/segmented control; reserve primary buttons for state-changing actions. |
| UX-003 | high | 1 | 2 | 3 | Continue translation has no guided path for a completed old run and a new chapter range. | Add a Continue Translation flow that proposes next scan gate and run ID after source boundary validation. |
| UX-004 | high | 1 | 2 | 3 | Batch controls expose internal fields before explaining the current state. | Show state summary and recommended action before fields. Generate sensible defaults where possible. |
| UX-005 | medium | 2 | 2 | 4 | Recovery controls are always present even when no failed block exists. | Hide or collapse recovery execution until a failed/suspicious block is selected. |
| UX-006 | medium | 2 | 1 | 3 | Report buttons are grouped by report names, not user questions. | Regroup reports by purpose: readiness, run completion, cleanliness, provider/failure, glossary. |
| UX-007 | medium | 1 | 2 | 3 | Glossary suggestion loading may call a provider, but the UI does not make this explicit. | Label model-backed suggestion calls and keep approval/rejection local and auditable. |
| UX-008 | medium | 1 | 2 | 3 | Setup and daily translation share one large dashboard, increasing cognitive load. | Keep Project Setup as a distinct task view or separate route. |
| UX-009 | low | 2 | 1 | 3 | Run picker previously showed layout fragility. | Keep single-column selector and add validation/error state when no run is loaded. |

## Task-First Redesign Specification
### Continue Translation
- Inputs shown only after current state is loaded.
- State shown:
  - current run
  - completion status
  - source boundary
  - whether glossary is scanned/approved
  - next safe action
- Primary actions:
  - `Start Glossary Scan`
  - `Continue Bounded Translation`
  - `Resume To Chapter`
- Required before action:
  - explicit run ID
  - explicit chapter range or boundary
  - exact command preview
  - stop condition summary

### Glossary Review
- Show queue state first: pending, approved, rejected, committed.
- Show each term with source context, first seen block, existing glossary intersections, and Thai options.
- Keep approve/reject as the only primary buttons.
- Model-backed suggestion calls must be labeled.

### Recover Block
- Default state: "No failed blocks" when none exist.
- If failures exist, show selectable failed blocks from status.
- Inspect view should show artifacts and recommended rerun stage.
- Rerun requires explicit confirmation and exact command preview.

### Reports
- Group by user question:
  - System readiness: preflight
  - Run completion: checkpoint/product-review
  - Output quality: cleanliness
  - Provider/failure review: provider usage
  - Glossary safety: glossary reports
- Mark report generation as artifact refresh, not pure read-only.

### Project Setup
- Separate from daily translation controls.
- Present as a short setup sequence:
  - create project
  - fill research profile
  - run preflight
  - validate source/fetch path
  - start scan-only gate

## Follow-Up Implementation Backlog
| priority | item | scope | target |
| --- | --- | --- | --- |
| P0 | Replace Primary Actions with task tabs and true primary action buttons | operator UI only | V6.5A |
| P0 | Build Continue Translation task panel with current-state guidance | operator UI + tests | V6.5B |
| P0 | Add explicit scan-first path for new Deep Sea Embers ranges | operator UI + status/snapshot helper if needed | V6.5C |
| P1 | Rework Glossary Review into a single decision workbench | operator UI + tests | V6.6 |
| P1 | Rework Recovery into failed-block-first workflow | operator UI + tests | V6.7 |
| P2 | Regroup Reports by user question | operator UI only | V6.8 |
| P2 | Move Project Setup into wizard-like task view | operator UI + tests | V6.9 |

## Acceptance Test Plan For Rebuilt Control Window
- Static checks:
  - HTML contains task views, not only panel groups.
  - Navigation controls are visually distinct from primary state-changing buttons.
  - Every state-changing button has exact command/scope preview.
- Runtime read-only checks:
  - `/api/bootstrap` loads default run.
  - run selector loads a specific run.
  - glossary queue loads without approval mutation.
  - inspect-block loads artifacts for a known completed block.
  - invalid state-changing payloads return 400.
- Browser-level checks:
  - open operator window on a test port.
  - click each navigation tab and verify visible task view changes.
  - click each read-only action and verify expected panel/result updates.
  - verify no console errors after load and after navigation clicks.
- State-changing checks:
  - use invalid payloads for guard checks by default.
  - use temporary project/workspace for setup actions.
  - do not run live provider translation or glossary suggestion calls without explicit approval.

## Stop Conditions For Implementation
- Any action can mutate state without explicit scope preview.
- Any task view hides a current failed block or manual action.
- Any UI change bypasses research readiness, bounded resume, or glossary approval guardrails.
- Any test claims UI behavior without checking the relevant rendered control or API response.
- Any workflow requires Codex memory to know the next button.

## Implementation Closeout
- closeout_status: accepted
- implementation_date: 2026-06-06
- files_changed_for_closeout:
  - `novel_pipeline/operator_ui.py`
  - `test_translation.py`
  - `IMPLEMENT_PLAN.md`
  - `PROJECT_BRAIN.md`
  - `OPERATOR_MANUAL.md`
  - `07_Reports/operator_workflow_audit_20260606.md`
- root_causes_confirmed:
  - the rendered operator JavaScript had invalid newline escaping, so the dashboard script could stop before binding buttons
  - deleted Primary Actions buttons still had live event listeners, which would break execution after the misleading buttons were removed
  - focus filtering treated every panel tagged with `all` as always visible, so task tabs did not actually reduce page complexity
  - sidebar run selector styling did not apply to `<select>`, causing fragile Run ID layout
- changes_landed:
  - removed misleading Primary Actions jump controls
  - added task-first `Task Guide`
  - tagged navigation buttons with `data-task-role="navigation"`
  - tagged read-only, state-changing, setup, report, and provider-assisted controls with explicit `data-action-role` values
  - fixed rendered JavaScript escaping for newline regex/string usage
  - fixed task focus filtering so `all` only shows all panels when the `All` task is selected
  - fixed sidebar Run ID input/select width
- verification:
  - `python -m compileall novel_pipeline`
  - `python test_translation.py`
  - rendered operator script checked with `node --check`
  - served operator window at `127.0.0.1:8778`
  - browser smoke verified default run load, task role counts, no Primary Actions/jump button, full-width Run ID controls, Glossary tab filtering, Recovery tab filtering, and no new console errors
- live_provider_calls: none
- live_translation_pipeline_actions: none
