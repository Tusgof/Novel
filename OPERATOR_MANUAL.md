# Operator Manual

Last updated: 2026-06-06

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
  - records: 163
  - fetched: ch019-ch023 complete.
  - glossary_scanned: ch019-ch023 complete.
  - glossary_approved: ch019-ch023 complete.
  - translating/refining/qa/formatting/completed: all expected ch019-ch023 blocks complete.
  - current failed blocks: none.
  - historical failed records: 9.
  - manual actions needed: none.
  - next effective action: none.
- outputs exist for `ch019` through `ch023`.
- ch024+: untouched.
- V3.11 complete: report automation command family now exists.
- V3.12 complete: glossary hardening report layer, scan-time guards, approval-stage queue revalidation, historical rejected-term guard, narrow QA glossary gate, and per-run guard verification now exist.
- V4.0 complete: local operator window now covers the practical single-novel workflow.
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
- Current V4.0 operator command:
  - `novel-pipeline --config ".system/config.yaml" operator --run-id batch-ch019-ch023-v1 --open-browser`
- Current operator window scope:
  - status dashboard
  - next safe action
  - research-profile editor for concise profile fields (`title`, `aliases`, `source_url`, `status`, `synopsis`, `tags`, `style_notes`, `reader_expectations`, `review_summary`, `last_reviewed_at`, `reviewed_by`, `terminology`, `reference_links`, `notes`)
  - block inspection
  - glossary candidate queue view
  - glossary suggestion loading with 2-3 Thai options
  - approve/reject glossary decisions
  - report generation
  - artifact viewing
  - novel-project scaffold form for `init-novel`
  - batch range start control for scan-only gate or bounded batch run
  - bounded resume control with required `until_chapter` or `until_block`
  - rerun-block control
- Operator guardrails:
  - init-novel requires explicit `project_root`, `title`, and `source_url`
  - research-profile save is limited to the concise profile fields surfaced in the UI and revalidates through `ResearchProfile.from_mapping(...)`
  - batch start requires explicit `run_id` and explicit chapter range
  - batch start supports only `glossary-scan` or bounded full-batch mode
  - resume requires `until_chapter` or `until_block`
  - resume always uses `manual_action_mode=stop`
  - glossary approval is limited to current queue terms only
- broader state-changing control beyond glossary approval, research-profile save, and bounded batch/resume/rerun is still intentionally absent
- V4.1 complete: multi-novel foundation now includes per-project scaffold and setup/fetch playbooks.
- V4.2 complete: multi-genre style profiles now provide structured preset guidance for refinement and QA.
- V4.3 complete: research-profile workflow now uses `RESEARCH_PROFILE.yaml`, a manual web-research playbook, and prompt context wiring for translation/refinement/QA.
- operator bootstrap/snapshot now carries the research-profile path plus readiness summary so the UI can surface pending, drafted, active, or missing states later.
- V4.4 complete: `novel-pipeline preflight` now checks provider executables, config/workspace integrity, research readiness, and git backup guardrails, and the operator window surfaces the same snapshot.
- V5.3 operator diagnostics improvement:
  - report buttons now include `preflight`
  - the preflight panel now shows workspace/config paths, research readiness state, per-provider resolved executable details, and git branch/head/origin/working-tree state
- V5.3 recovery drill improvement:
  - report buttons now include `recovery-drill`
  - recovery drill verifies canonical docs are tracked/restorable from `HEAD`
  - recovery drill verifies runtime directories remain ignored and untracked
- V5.3 operator friction reduction:
  - bootstrap snapshot now includes copyable command hints for preflight, status, reports, and first-failed-block inspection
  - the operator window now shows quick links to canonical docs and high-value reports when those files exist
- V5.3 restore walkthrough:
  - `00_Templates/Recovery-Drill-Checklist.md` now defines the exact restore sequence for canonical docs
  - the checklist explicitly separates canonical-doc restore from runtime artifact handling
- current preflight baseline: `ready` on 2026-05-10 after V5.1/V5.2 verification (working tree clean, research readiness `active / ready`).
- V5.0 complete: the operator window now covers practical end-to-end local workflow from project scaffold through research profile maintenance, glossary approval, bounded batch execution, recovery, reports, and final-output review.
- V5.1 complete: product-complete review and verification now exists through `report product-review`.
- V5.2 complete: canonical docs and memory cleanup are closed; the root doc set is now explicit and legacy overlapping docs are retired.
- V5.3 complete: preflight diagnostics, recovery drill reporting, operator recovery hints, quick links, and canonical recovery checklist are now part of the accepted hardening baseline.
- V5.4 complete: generated report refreshes under `07_Reports/` no longer degrade preflight/product-review by themselves.
- V6.0 complete: `Operator Control Dashboard`.
- V6.0 intent:
  - denser translation control dashboard
  - dedicated glossary approval workbench
  - clearer bounded recovery and block-inspection surface
- V6.0A complete:
  - run selector from known run IDs
  - preflight/provider status strip
  - run overview panel for scope, blocker, next action, and chapter pressure
  - chapter progress matrix sorted by pressure with next pending stage visibility
  - current blocker panel
  - recent activity log
- V6.0B complete:
  - batch, resume, and rerun controls now show exact CLI-equivalent previews before execution
  - each control shows explicit scope and guardrail text
  - action results echo the previewed command for audit trail clarity
- V6.0C complete:
  - glossary queue now shows batch closure progress
  - each term shows intersecting approved/rejected/quarantine/proposed note history
  - suggestion view includes first-seen location, history context, and selected decision preview
- V6.0D complete:
  - inspect workbench now shows source, literal, refined, QA, and formatted artifact links together
  - latest stage state and formatted validation findings are visible in one view
  - inspect can prefill rerun-block targets into the recovery controls
- V6.0E complete:
  - dashboard now shows an `Accepted Guardrails` panel
  - the accepted bounded-action model is visible in one place:
    - allowed state-changing actions only
    - bounded translation rules
    - visible report kinds
  - no broad unbounded execution action was added while closing the dashboard milestone
- V6.1 complete: `System Review, Verification, And Cleanup`.
- V6.1A complete:
  - read-only audit captured cleanup candidates before any destructive changes
  - top cleanup targets are:
    - benchmark/test helper scripts in `scripts/`
    - mixed active vs historical files in `07_Reports/`
    - canonical doc naming inconsistency around `IMPLEMENT_PLAN.md`
    - disposable local cache such as `__pycache__/`
- V6.1B complete:
  - active code, templates, tests, and canonical docs now use `IMPLEMENT_PLAN.md` consistently
  - the canonical roadmap path is normalized for recovery and quick-link flows
- V6.1C complete:
  - benchmark/history reports now live under `07_Reports/archive/`
  - benchmark/debug helper scripts now live under `scripts/archive/benchmarks/`
  - disposable local cache such as `__pycache__/` has been removed from the active repo surface
- V6.1D complete:
  - compile/tests passed after cleanup
  - `preflight` returned `ready`
  - `recovery-drill` remained `accepted`
  - `product-review` remained accepted after cleanup
- V6.2 complete:
  - dashboard scan speed and report workspace clarity improved without changing the bounded execution model
  - `07_Reports/` root now presents operational reports only; historical run evidence lives under `07_Reports/archive/history/`
  - the operator window now shows a dedicated `Report Workspace` panel with active vs archive separation
- V6.3 complete:
  - the dashboard now supports workflow focus modes: `Current Run`, `Glossary`, `Recovery`, `Reports`, `Setup`, and `All`
  - batch start and bounded resume are grouped under `Batch Controls`
  - rerun-block and action feedback are grouped under `Recovery Controls`
  - glossary queue and glossary decision now form a tighter glossary task surface
  - project scaffold and research editing are moved under `Project Setup` instead of the daily run path
  - report generation now lives in a dedicated `Report Controls` panel inside the main workspace
- V6.4 complete:
  - the operator control window now uses task-first modes: `Continue Translation`, `Glossary Review`, `Recover Block`, `Reports`, `Project Setup`, and `All`
  - misleading Primary Actions jump buttons were removed; navigation controls are secondary and action buttons stay inside task panels
  - control roles are explicit in the HTML for navigation, read-only actions, state-changing actions, setup actions, report actions, and provider-assisted glossary suggestions
  - Run ID input/select layout is fixed in the sidebar
  - audit report: `07_Reports/operator_workflow_audit_20260606.md`
- V6.5 complete:
  - the first working surface is now `Daily Home`: current run, blocker, next safe action, and task guidance
  - long helper copy was removed from the sidebar and primary task panels
  - technical diagnostics, command hints, guardrails, and preflight details are collapsed under `Technical Details`
  - recovery execution controls are hidden when the loaded run has no failed/manual block
  - report buttons are grouped by operator question: system readiness, run completion, output cleanliness, provider issue, and glossary safety
  - audit report: `07_Reports/operator_ui_text_surface_audit_20260606.md`
- V6.6 complete:
  - dashboard shows eight display-only employee cards: `000 Ferryman`, `001 Libra`, `002 Quill`, `003 Vesper`, `004 Corvus`, `005 Loom`, `006 Archivist`, and `007 Warden`
  - employee cards describe real mapped stages/actions and show provider/model routes; ledger/config stage names remain canonical
  - provider smoke testing is explicit and user-triggered only; normal dashboard load remains read-only
  - long-running actions now surface loading/status feedback with current employee/action/provider context
  - formatting is hybrid gated: configured AI formatter first, deterministic validation always, local formatter as fallback/cleanup
  - design rules now live in `DESIGN.md`

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

Preflight:

```powershell
novel-pipeline --config ".system/config.yaml" preflight
novel-pipeline --config ".system/config.yaml" report preflight
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
novel-pipeline --config ".system/config.yaml" report product-review --run-id batch-ch019-ch023-v1
novel-pipeline --config ".system/config.yaml" report preflight
novel-pipeline --config ".system/config.yaml" report recovery-drill
```

Current generated artifacts:

- `07_Reports/checkpoint_batch-ch019-ch023-v1.md`
- `07_Reports/cleanliness_batch-ch019-ch023-v1_ch019-ch020-ch021-ch022-ch023.md`
- `07_Reports/provider_usage_batch-ch019-ch023-v1.md`
- `07_Reports/glossary_decisions_batch-ch019-ch023-v1.md`
- `07_Reports/glossary_conflicts_batch-ch019-ch023-v1.md`
- `07_Reports/glossary_audit_batch-ch019-ch023-v1.md`
- `07_Reports/glossary_guard_batch-ch019-ch023-v1.md`
- `07_Reports/preflight_report.md`
- `07_Reports/recovery_drill.md`
- historical and benchmark artifacts are intentionally moved under `07_Reports/archive/`
- active dashboard work should treat `07_Reports/` root as operational surface and `07_Reports/archive/` as read-only history
- `00_Templates/Recovery-Drill-Checklist.md`

V4.1 setup artifacts:

- `00_Templates/Novel-Profile.yaml`
- `00_Templates/Research-Profile.yaml`
- `NOVEL_SETUP_PLAYBOOK.md`
- `FETCH_ADAPTER_PLAYBOOK.md`
- `RESEARCH_PROFILE_PLAYBOOK.md`

Canonical root docs:

- `PROJECT_BRAIN.md`
- `IMPLEMENT_PLAN.md`
- `OPERATOR_MANUAL.md`

Retired root docs:

- `MASTER_PLAN.md`
- `REPORT.md`
- `SUMMARY.md`

V4.2 style profile artifacts:

- `.system/style_profiles.yaml`
- structured fields now used by prompts:
  - `genre_label`
  - `tone`
  - `naming_notes`
  - `narration_density`
  - `glossary_categories`
  - `qa_criteria`
- current preset keys:
  - `default`
  - `dark_fantasy`
  - `xianxia_wuxia`
  - `modern_urban`
  - `sci_fi`
  - `horror`
  - `romance_drama`
  - `deep_sea_embers`

V4.3 research artifacts:

- `RESEARCH_PROFILE.yaml` at the project root
- `00_Templates/Research-Profile.yaml`
- `RESEARCH_PROFILE_PLAYBOOK.md`
- current prompt wiring uses `research_context` in literal translation, refinement, and QA

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

## Create A New Novel Project

Use this only when you are setting up a different novel, not when continuing Deep Sea Embers.

Required inputs:

- title
- source TOC/index URL
- source language
- target language
- genre
- adapter choice

Command:

```powershell
novel-pipeline --config ".system/config.yaml" init-novel `
  --project-root "D:\Fogust\Workspace\Novel\<New Project Folder>" `
  --title "<Primary Title>" `
  --source-url "<TOC URL>" `
  --novel-id "<novel-id>" `
  --alias "<Alt Title>" `
  --source-language zh `
  --target-language th `
  --genre "<genre>" `
  --adapter "<adapter>" `
  --style-profile "<style_profile>"
```

Style selection behavior:

- explicit `--style-profile` wins
- otherwise `--genre` is normalized and matched to a known preset when possible
- otherwise the scaffold falls back to the template project's default style profile

Expected result:

- new project folder exists
- `NOVEL_PROFILE.yaml` exists
- `.system/config.yaml` exists
- copied `prompts/` and `00_Templates/` exist
- isolated state folders exist

Then follow:

1. `NOVEL_SETUP_PLAYBOOK.md`
2. `RESEARCH_PROFILE_PLAYBOOK.md`
3. `FETCH_ADAPTER_PLAYBOOK.md`

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
