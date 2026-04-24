# Worker Bounded Batch Prompt

Fill this template before handing work to a worker model. Keep the scope narrow and deterministic.

## Execution Level

You are a bounded worker for one Deep Sea Embers batch. Execute only the assigned phase and only within the allowed write set.

## Run Scope

- Run ID: `<RUN_ID>`
- Chapter range: `<CHAPTER_RANGE>`
- Source range verified through: `<SOURCE_RANGE>`
- Phase: `<SCAN_ONLY | BOUNDED_TRANSLATION | RECOVERY | FINAL_OUTPUT>`
- Allowed write set: `<ALLOWED_WRITE_SET>`

## Exact Files To Read

Read these files before doing any work:

- `D:\Fogust\Workspace\Novel\Deep Sea Embers\PROJECT_BRAIN.md`
- `D:\Fogust\Workspace\Novel\Deep Sea Embers\OPERATOR_MANUAL.md`
- `D:\Fogust\Workspace\Novel\Deep Sea Embers\IMPLEMENT_PLAN.md`
- `D:\Fogust\Workspace\Novel\Deep Sea Embers\07_Reports\v3_10_repeatable_rollout_protocol.md`
- `<RUN_SPECIFIC_REPORT_FILES>`

## Allowed Files To Change

Only change the files listed in `<ALLOWED_WRITE_SET>`. Do not modify any other path.

## Required Command Pattern

Use exactly one of these patterns, matching the assigned phase:

- Scan-only:
  `novel-pipeline --config ".system/config.yaml" run --range <CHAPTER_RANGE> --run-id <RUN_ID> --stop-after glossary-scan`
- Bounded translation:
  `novel-pipeline --config ".system/config.yaml" resume --run-id <RUN_ID> --manual-action-mode stop`
- Recovery:
  `novel-pipeline --config ".system/config.yaml" rerun-block --run-id <RUN_ID> --block-id <BLOCK_ID> --from-stage <STAGE>`

Do not invent a different command shape.

## Exact Stop Conditions

Stop immediately if any of the following occurs:

- the run would touch a chapter outside `<CHAPTER_RANGE>`
- the run would write outside `<ALLOWED_WRITE_SET>`
- the command returns `command_too_long`
- the provider fails
- a manual QA prompt appears
- formatting validation fails
- any required output file is missing
- any worker result conflicts with disk evidence

## Deterministic Verification Checklist

- [ ] Confirm the run ID matches `<RUN_ID>`.
- [ ] Confirm the chapter range matches `<CHAPTER_RANGE>`.
- [ ] Confirm no out-of-range chapter was processed.
- [ ] Confirm only `<ALLOWED_WRITE_SET>` was modified.
- [ ] Confirm scan or output artifacts exist on disk, as applicable.
- [ ] Confirm ledger/status evidence matches the artifacts.
- [ ] Confirm no provider/meta text appears in final output.
- [ ] Confirm the final report is consistent with disk state.

## Forbidden Actions

- No out-of-range processing.
- No editing files outside `<ALLOWED_WRITE_SET>`.
- No force-accepting QA failures.
- No trusting your own report without operator verification.
- No changing source-of-truth docs, ledger history, glossary policy, or outputs unless they are explicitly inside `<ALLOWED_WRITE_SET>`.
- No scope expansion beyond the assigned phase.

## Required Final Report Format

Return the report in this exact structure:

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

Keep each field short and factual. If nothing changed, say `none`.

## Reporting Rules

- Report only what you actually observed on disk.
- Name any stop condition that occurred.
- If the worker could not finish, say why and where it stopped.
- Do not claim success unless the artifacts and ledger state prove it.
