# Operator Manual

Last updated: 2026-04-28

This is the practical runbook. It should help the operator proceed without guessing.

## Current Status

- V3.7 complete: ch004-ch008.
- V3.8 complete: ch009-ch018.
- V3.9 complete: `batch-ch019-ch023-v1`.
- ch001-ch023 outputs exist.
- V3.10 protocol artifacts exist:
  - `00_Templates/Batch-Rollout-Checklist.md`
  - `00_Templates/Worker-Bounded-Batch-Prompt.md`
  - `07_Reports/v3_10_repeatable_rollout_protocol.md`
- V3.10 complete: repeatable rollout protocol package is ready.
- Current V3.9 final state:
  - fetched: ch019-ch023 complete.
  - glossary_scanned: ch019-ch023 complete.
  - glossary_approved: ch019-ch023 complete.
  - translating/refining/qa/formatting/completed: all expected ch019-ch023 blocks complete.
  - current failed blocks: none.
  - manual actions needed: none.
- outputs exist for `ch019` through `ch023`.
- ch024+: untouched.
- V3.11 complete: report automation command family now exists.
- V3.12 complete: glossary hardening report layer, scan-time guards, approval-stage queue revalidation, historical rejected-term guard, narrow QA glossary gate, and per-run guard verification now exist.
- V3.12 QA-stage glossary gate now blocks the narrow case where literal translation already used an approved Thai term and refinement removes it.
- Current scan-time guard behavior:
  - exact quarantine/rejected/deprecated terms are filtered before queue entry
  - exact historical rejected terms from prior glossary approvals are filtered before queue entry
  - narrow approved-term noise such as `是失乡号` is filtered
  - substring fragments that never occur standalone in a block are filtered
- Current approval-stage guard behavior:
  - older glossary scan artifacts are revalidated against the current deterministic queue before prompting or writing notes
- Current V3.12 verification artifact:
  - `07_Reports/glossary_guard_batch-ch019-ch023-v1.md`
- Next safe action: start V4.0 operator-product work from the current stable guard baseline, not a new translation batch.

## Standard Preflight

Run from:

```powershell
cd "D:\Fogust\Workspace\Novel\Deep Sea Embers"
$env:PYTHONIOENCODING='utf-8'
```

Compile/test:

```powershell
python -m compileall novel_pipeline
python test_translation.py
```

Status:

```powershell
novel-pipeline --config ".system/config.yaml" status --run-id batch-ch019-ch023-v1
```

Generated verification reports:

```powershell
novel-pipeline --config ".system/config.yaml" report checkpoint --run-id batch-ch019-ch023-v1
novel-pipeline --config ".system/config.yaml" report cleanliness --run-id batch-ch019-ch023-v1
novel-pipeline --config ".system/config.yaml" report provider-usage --run-id batch-ch019-ch023-v1
novel-pipeline --config ".system/config.yaml" report glossary-decisions --run-id batch-ch019-ch023-v1
novel-pipeline --config ".system/config.yaml" report glossary-conflicts --run-id batch-ch019-ch023-v1
novel-pipeline --config ".system/config.yaml" report glossary-audit --run-id batch-ch019-ch023-v1
novel-pipeline --config ".system/config.yaml" report glossary-guard --run-id batch-ch019-ch023-v1
```

Current generated artifacts:

- `07_Reports/checkpoint_batch-ch019-ch023-v1.md`
- `07_Reports/cleanliness_batch-ch019-ch023-v1_ch019-ch020-ch021-ch022-ch023.md`
- `07_Reports/provider_usage_batch-ch019-ch023-v1.md`
- `07_Reports/glossary_decisions_batch-ch019-ch023-v1.md`
- `07_Reports/glossary_conflicts_batch-ch019-ch023-v1.md`
- `07_Reports/glossary_audit_batch-ch019-ch023-v1.md`
- `07_Reports/glossary_guard_batch-ch019-ch023-v1.md`

If CLI is unavailable, inspect:

```text
06_Logs/run_ledger.jsonl
04_Work/
05_Output/
```

## Scan-Only Glossary Gate

Use for new chapter ranges before translation:

```powershell
novel-pipeline --config ".system/config.yaml" run --range ch019-ch023 --run-id batch-ch019-ch023-v1 --stop-after glossary-scan
```

Expected:

- fetch records appended
- glossary_scanned records appended
- batch artifact exists under `04_Work/_batch/<run_id>/glossary_scan.json`
- no glossary_approved records yet
- no translation/refinement/QA/formatting records
- no final outputs

The reusable operator checklist for this gate is `00_Templates/Batch-Rollout-Checklist.md`.

## Glossary Approval Gate

Before translation:

1. Review `07_Reports/glossary_classification_<run_id>.md`.
2. Ask user for ambiguous term decisions.
3. Create/update only approved glossary notes.
4. Append `glossary_approved` records with exact chapter block IDs:
   - `ch019`, `ch020`, etc.
5. Verify no translation records were created.

Current V3.9 approved terms:

- `实太阳神` -> `สุริยเทพที่แท้จริง`
- `面具神` -> `เทพหน้ากาก`

Use `00_Templates/Worker-Bounded-Batch-Prompt.md` for the worker handoff after this gate is closed.

## Bounded Resume

Do not run long blind resumes with noninteractive workers. Use bounded checkpoints.

Recommended next step after V3.9:

- Do not start a new Deep Sea Embers translation range until new source exists beyond `ch023`.
- Use the completed V3.9 run as the reference case for protocol extraction and operator checklist design.
- Use `07_Reports/v3_10_repeatable_rollout_protocol.md` as the repeatable rollout reference.

General command:

```powershell
novel-pipeline --config ".system/config.yaml" resume --run-id batch-ch019-ch023-v1
```

If recovering a single block:

```powershell
novel-pipeline --config ".system/config.yaml" rerun-block --run-id batch-ch019-ch023-v1 --block-id <block-id> --from-stage <stage>
```

## Validation After A Block Completes

Inspect:

- `04_Work/<chapter>/<block>.literal.json`
- `04_Work/<chapter>/<block>.refined.json`
- `04_Work/<chapter>/<block>.qa.json`
- `04_Work/<chapter>/<block>.formatted.json`
- `06_Logs/run_ledger.jsonl`
- `07_Reports/v3_10_repeatable_rollout_protocol.md` if the run changes operator procedure or recovery rules

Check:

- QA passed
- formatting completed
- completed record exists
- no provider/meta/error text
- no Han Chinese in Thai body
- no wrong glossary variants
- no quote-only lines
- dialogue quote marks are not lost after formatting

## Handling QA Hard-Fail

If QA reports semantic omission or meaning drift:

1. Stop.
2. Read source, literal, refined, QA.
3. Decide whether deterministic artifact repair is enough.
4. If repair is made, modify the narrowest artifact only.
5. Rerun from QA or the failed stage.
6. Verify formatted output afterward.

Do not force-accept without explicit user/Codex decision.

## Handling Noninteractive EOF

If a worker reports `EOF when reading a line`, it likely hit a manual QA prompt.

Action:

- Stop the batch.
- Inspect the QA artifact.
- Do not resume blindly until a repair/decision is made.

## Handling Claude Crash

Known error:

- return code `3221225786`
- empty stderr/stdout

Action:

- retry may succeed
- if repeated, allow GPT-5.4 fallback for refinement
- GPT output must pass deterministic checks and Qwen QA

## Handling Gemini command_too_long

Known risk:

- Gemini argv transport can hit command-line length limits, especially as QA fallback.
- Preflight exists, but fallback incidents can still occur.

Action:

- use bounded QA-stage rerun if Qwen primary can succeed
- do not switch literal translation to Claude
- if repeated, stop and report

## Worker Restrictions

Do not use Elephant or Nemotron for state-changing operations.

Forbidden:

- ledger append
- glossary approval
- artifact modification
- code/config edits
- resume/rerun
- translation checkpoints
- force-accept decisions

Reason: both produced false completion reports in V3.9.

## What Not To Do

- Do not process ch024+ during `batch-ch019-ch023-v1`.
- Do not create final output before all chapter blocks complete.
- Do not edit ledger except append-only deliberate records.
- Do not delete historical failed records.
- Do not trust provider/worker reports without disk verification.
- Do not compress project docs into short summaries.

## How To Start The Next Bounded Batch

Use this generic sequence for any future range once source exists and the range has been approved:

1. Confirm the verified source boundary for the range.
2. Choose the batch size using `00_Templates/Batch-Rollout-Checklist.md`.
3. Run the scan-only gate for the exact range.
4. Review the scan/classification report and complete glossary approval.
5. Hand the worker `00_Templates/Worker-Bounded-Batch-Prompt.md` with the exact run ID, range, and allowed write set filled in.
6. Stop the worker on any listed stop condition.
7. Verify final outputs and ledger evidence before signoff.

## End-Of-Batch Gate

For ch019-ch023 completion:

- all expected blocks complete
- outputs exist for ch019-ch023
- current failed blocks none
- no ch024+ processing
- all cleanliness checks pass
- spot-check report exists
- docs updated:
  - `PROJECT_BRAIN.md`
  - `IMPLEMENT_PLAN.md`
  - `OPERATOR_MANUAL.md`
  - `00_Templates/Batch-Rollout-Checklist.md`
  - `00_Templates/Worker-Bounded-Batch-Prompt.md`
  - `07_Reports/v3_10_repeatable_rollout_protocol.md`
  - root `D:\Fogust\Workspace\Novel\AGENTS.md` remains the active general agent policy
