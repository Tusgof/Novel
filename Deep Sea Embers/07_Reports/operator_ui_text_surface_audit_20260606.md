# Operator UI Text And Surface Audit - 2026-06-06

## Scope
- milestone: V6.5 Operator UI/UX Rebuild For Normal Users
- source audited: `novel_pipeline/operator_ui.py`
- live_provider_calls: none
- live_translation_pipeline_actions: none

## Verdict
The operator window has the correct backend guardrails, but the visible UI still reads like operational documentation. The rebuild should reduce visible copy, make `Continue Translation` the daily home, and move technical diagnostics behind details unless the selected task needs them.

## Surface Decisions
| surface | decision | reason |
| --- | --- | --- |
| Sidebar product description | remove/shorten | repeated purpose text; does not help the next click |
| Run selector helper text | remove | label, placeholder, selector, and buttons already explain the control |
| Task helper paragraph | remove | task buttons are self-explanatory |
| Navigation policy note | remove | belongs in docs, not the main UI |
| Task Workspace header | shorten | navigation should not take a full explanatory block |
| Metrics/status strip | move to details | useful diagnostics, but not primary daily action |
| Run Overview | keep visible | answers current run/blocker/next action |
| Task Guide | keep visible, shorten | should lead to the next safe action |
| Batch Controls | rename/shorten | should read as Start Batch / Continue To Boundary |
| Chapter Dashboard | keep visible in daily task | useful progress evidence |
| Glossary Workbench | shorten | approval task needs queue and decision, not long instructions |
| Glossary Decision | shorten | keep provider-assisted warning close to Load options |
| Recovery Controls | hide by default when no failed/manual block exists | recovery is noise during normal translation |
| Project Setup | keep separate task | lower-frequency workflow should not compete with daily translation |
| Current Blocker / Safe Next Action / Manual Actions | merge into first screen summary | currently duplicates Run Overview and Task Guide |
| Reports | regroup by user question | report names are implementation details |
| Research Readiness / Recovery Hints / Guardrails / Preflight / Activity | move to details/context | useful for debugging, too noisy for normal operation |

## Copy Rules For Implementation
- Keep visible subtitles only when they prevent a real mistake.
- Use user task labels first; keep CLI/action names in previews or details.
- Replace long empty states with short states: `No run loaded.`, `No pending terms.`, `No current failures.`
- Prefer one primary action per task area.
- Keep provider-backed glossary suggestion clearly labeled before the user clicks it.

## Acceptance Checks
- First viewport shows current run, blocker, and next action.
- `Continue Translation` is the default daily home.
- Technical status exists but is collapsed by default.
- Recovery execution controls are hidden when there is no failed/manual block.
- Reports are grouped by operator question, not raw report kind names.
- Browser smoke verifies task switching and no console errors.

## Implementation Closeout
- closeout_status: accepted
- implementation_date: 2026-06-06
- files_changed_for_closeout:
  - `novel_pipeline/operator_ui.py`
  - `test_translation.py`
  - `IMPLEMENT_PLAN.md`
  - `PROJECT_BRAIN.md`
  - `OPERATOR_MANUAL.md`
  - `07_Reports/operator_ui_text_surface_audit_20260606.md`
- changes_landed:
  - removed long sidebar helper text
  - replaced the old top-heavy overview stack with `Daily Home`
  - kept current run, blocker, next safe action, and task guidance above the main controls
  - moved metrics, status strip, command hints, guardrails, and preflight diagnostics into collapsed `Technical Details`
  - renamed daily actions to user-task labels such as `Start Batch` and `Continue To Boundary`
  - hid recovery execution controls when the loaded run has no current failed/manual block
  - grouped report buttons by operator question
  - preserved bounded backend action IDs and guardrails
- verification:
  - `python -m compileall novel_pipeline`
  - `python test_translation.py`
  - rendered operator script checked with `node --check`
  - served operator window at `127.0.0.1:8765`
  - browser smoke verified default run load, daily home visibility, task switching, collapsed technical details, hidden recovery execution, report grouping, no old helper copy, no Primary Actions, and no new console errors
- live_provider_calls: none
- live_translation_pipeline_actions: none
