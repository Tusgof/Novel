# Worker Bounded Batch Prompt

Fill this template before delegating one bounded Immortality System task.

## Run Scope

- Run ID: `<RUN_ID>`
- Chapter range: `<CHAPTER_RANGE>`
- Source range verified through: `<SOURCE_RANGE>`
- Phase: `<SCAN_ONLY | BOUNDED_TRANSLATION | RECOVERY | FINAL_OUTPUT>`
- Allowed write set: `<ALLOWED_WRITE_SET>`

## Required Context

Read the root control documents:

- `D:\Fogust\Workspace\Novel\PROJECT_BRAIN.md`
- `D:\Fogust\Workspace\Novel\IMPLEMENT_PLAN.md`
- `D:\Fogust\Workspace\Novel\ARCHITECTURE.md`
- `D:\Fogust\Workspace\Novel\Immortality System\NOVEL_PROFILE.yaml`
- `D:\Fogust\Workspace\Novel\Immortality System\RESEARCH_PROFILE.yaml`
- `<RUN_SPECIFIC_REPORT_FILES>`

## Required Command Pattern

- Scan-only: `novel-pipeline --config ".system/config.yaml" run --range <CHAPTER_RANGE> --run-id <RUN_ID> --stop-after glossary-scan`
- Bounded resume: `novel-pipeline --config ".system/config.yaml" resume --run-id <RUN_ID> --manual-action-mode stop`
- Recovery: `novel-pipeline --config ".system/config.yaml" rerun-block --run-id <RUN_ID> --block-id <BLOCK_ID> --from-stage <STAGE>`

## Exact Stop Conditions

Stop if the run would touch a chapter outside the declared range, write outside the
allowed set, return `command_too_long`, encounter provider failure, show a manual QA
prompt, fail formatting validation, miss an artifact, or conflict with disk evidence.

## Verification

- [ ] Run ID and range match.
- [ ] No out-of-range chapter was processed.
- [ ] Only the allowed write set changed.
- [ ] Ledger/status matches artifacts.
- [ ] Final output has no provider/meta text or Chinese body text.
- [ ] Final report states the actual outcome and next safe step.

## Forbidden Actions

- No out-of-range processing.
- No force-accepting QA failures.
- No changing root control docs, glossary policy, or final output outside the write set.
- No scope expansion.

## Required Final Report

```text
RUN_ID:
CHAPTER_RANGE:
PHASE:
COMMANDS_RUN:
FILES_CHANGED:
FILES_CHECKED:
STOP_CONDITIONS_ENCOUNTERED:
VERIFICATION_RESULTS:
OUTCOME:
BLOCKERS:
NEXT_SAFE_STEP:
```
