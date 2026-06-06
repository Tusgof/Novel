# Project Brain: Deep Sea Embers Translation Pipeline

Last updated: 2026-06-06
Last verified: 2026-06-06 after V6.5 operator UI/UX rebuild with compile/tests, rendered-script syntax check, served operator window, browser smoke on `127.0.0.1:8765`, collapsed technical details, hidden recovery execution when no failures exist, and no new console errors.

This file is the project constitution, architecture map, and current operational memory. It should preserve the project goal, design principles, verified state, safety rules, recovery lessons, and pointers to detailed documents. Keep reports, long logs, and implementation detail in their dedicated files.

## Project Definition

Purpose: build a semi-automated Chinese-to-Thai novel translation production system that can preserve meaning, keep terminology consistent, recover from provider failures, and let one operator run controlled chapter batches without fragile manual memory.

Primary operator: the user, assisted by Codex as architect/reviewer and bounded worker models for implementation or execution.

Current novel: Deep Sea Embers.

Long-term product scope: support multiple novels and multiple genres through per-novel configuration, source adapters, style profiles, isolated artifacts, and an operator UI/window.

Out of scope for now:

- fully automatic publishing without human review
- silent force-accept of semantic QA failures
- unbounded background translation runs with no checkpoints
- using unreliable free models for state-changing work
- polishing UI aesthetics before the workflow is reliable

## Success Criteria

The current pipeline is useful when:

- a chapter range can be fetched, scanned, glossary-approved, translated, refined, QA-checked, formatted, and assembled with auditable artifacts
- every stage can be resumed or rerun without corrupting prior work
- final outputs are clean Thai Markdown with no provider/meta text, no unintended Chinese body text, no wrong glossary variants, and no quote-only lines
- semantic omissions and meaning drift are caught before final assembly or explicitly reviewed by the user
- provider crashes, quota limits, command-length errors, and manual QA prompts have safe recovery paths

The broader product is complete enough for real use when:

- a new novel can be configured without code edits
- novel/genre profiles can guide style and terminology
- the user can run scan, approval, translation, recovery, and reports from a practical local operator interface
- documentation and reports update without ad hoc manual rewriting
- worker models cannot silently damage source-of-truth state

## Architecture Overview

The system is a staged, auditable pipeline:

```text
source adapter
  -> source validation
  -> block splitting
  -> glossary scan
  -> glossary approval
  -> literal translation
  -> literary refinement
  -> QA judgment
  -> formatting
  -> chapter assembly
  -> reports and documentation sync
```

Core components:

- `novel_pipeline/`: Python package and CLI.
- `novel_pipeline/pipeline.py`: main orchestration, resume, status, rerun behavior.
- `novel_pipeline/stages/`: fetch, glossary, translation, refinement, QA, formatting.
- `.system/`: pipeline config, provider routing, retry/timeout policy, style profiles.
- `01_Glossary/`: approved/deprecated terminology notes.
- `03_Raw/`: fetched source cache.
- `04_Work/`: per-block and batch artifacts.
- `05_Output/`: final chapter Markdown.
- `06_Logs/run_ledger.jsonl`: append-only execution ledger.
- `07_Reports/`: active operational reports at the root; historical/benchmark artifacts under `07_Reports/archive/`.

State model:

- artifacts record stage outputs
- ledger records stage commitments
- status should be inferred from latest valid state, not naive failed-record counts
- historical failed records remain because the ledger is append-only

## Design Principles

- Correctness before speed.
- Human approval before glossary or semantic-risk decisions.
- Append-only audit trail over destructive edits.
- Deterministic validation before trusting provider judgment.
- Bounded checkpoints over long blind runs.
- Recoverability over one-shot automation.
- Glossary and meaning consistency over model creativity.
- Codex owns architecture and verification; workers execute bounded instructions.
- Worker reports are claims until disk state proves them.
- Multi-novel and multi-genre support must be designed in, not bolted on after the first novel.

## Canonical Document Set

Root docs that remain canonical:

- `PROJECT_BRAIN.md`: durable project memory, architecture, verified state, guardrails, and recovery lessons
- `IMPLEMENT_PLAN.md`: milestone roadmap from the current verified state forward
- `OPERATOR_MANUAL.md`: practical operator runbook and command policy

Operational supporting docs that stay separate:

- `NOVEL_SETUP_PLAYBOOK.md`: new-project setup workflow
- `FETCH_ADAPTER_PLAYBOOK.md`: adapter design/validation workflow
- `RESEARCH_PROFILE_PLAYBOOK.md`: research collection workflow
- `00_Templates/`: reusable checklists and scaffolds
- `07_Reports/`: active operational evidence at the root plus archived historical/benchmark evidence under `07_Reports/archive/`

Retired root docs:

- `MASTER_PLAN.md`: superseded by `PROJECT_BRAIN.md` plus `IMPLEMENT_PLAN.md`
- `REPORT.md`: stale point-in-time snapshot superseded by current reports and `PROJECT_BRAIN.md`
- `SUMMARY.md`: stale point-in-time snapshot superseded by current reports and `PROJECT_BRAIN.md`

Rule:

- do not recreate overlapping root summary/plan docs
- if a new durable rule or architectural fact matters, put it in `PROJECT_BRAIN.md`
- if a new future milestone matters, put it in `IMPLEMENT_PLAN.md`
- if a new execution procedure matters, put it in `OPERATOR_MANUAL.md`

## Improvement Backlog Scoring

Use two axes for prioritization:

- Ease: `0` hard, `1` medium, `2` easy.
- Importance: `0` low, `1` medium, `2` high.

Score = Ease + Importance. Items with score below `2` are deferred.

| Issue | Ease | Importance | Score | Status |
| --- | --- | --- | --- | --- |
| Manual-action stop mode | 2 | 2 | 4 | implemented 2026-04-20 |
| Effective status visibility | 2 | 2 | 4 | implemented 2026-04-20 |
| Basic post-format validation | 1 | 2 | 3 | implemented 2026-04-20 |
| Provider usage/cost report | 1 | 1 | 2 | later |
| Bounded resume until chapter/block | 0 | 2 | 2 | implemented 2026-04-20 |
| Inspect-block command | 1 | 1 | 2 | implemented 2026-04-20 |
| QA warning pass/fail semantics | 2 | 2 | 4 | implemented 2026-04-23 |
| Multi-novel config/profile | 0 | 2 | 2 | later |
| Operator UI/window | 0 | 2 | 2 | later |
| Cosmetic UI polish | 1 | 0 | 1 | deferred |

Implemented runtime safety controls:

- `resume --manual-action-mode stop` prevents noninteractive EOF by exiting with manual-action status instead of prompting.
- `resume --until-chapter <chapter_id>` and `resume --until-block <block_id>` allow bounded production checkpoints.
- `inspect-block --run-id <run_id> --block-id <block_id>` is a read-only block inspection tool.
- `status` now prints current failed blocks, historical failed records, and next effective action.
- formatting now rejects provider/meta leakage, Han Chinese text, and quote-only lines before committing successful formatted artifacts.
- QA reports now allow deterministic warning findings such as `sentence_drop` to remain visible without blocking a Qwen `PASS`; deterministic `error` findings and AI judge failure findings still block.

## Current Verified State

Completed:

- ch001-ch003: earlier baseline outputs exist.
- V3.7 complete: `batch-ch004-ch008-v2`
  - 28/28 blocks complete.
  - ch004-ch008 outputs exist.
  - deterministic checks and spot-check passed.
- V3.8 complete: `batch-ch009-ch018-v1`
  - 53/53 blocks complete.
  - ch009-ch018 outputs exist.
  - current failed blocks: none.
  - historical failed ledger records are expected.

Active:

- V3.9 complete: `batch-ch019-ch023-v1`
- glossary scan-only gate: complete
- glossary approval gate: complete
- approved terms:
  - `实太阳神` -> `สุริยเทพที่แท้จริง`
  - `面具神` -> `เทพหน้ากาก`
- correct `glossary_approved` ledger records exist with block IDs `ch019`, `ch020`, `ch021`, `ch022`, `ch023`
- ch019: 5/5 complete, output exists
- ch020: 5/5 complete, output exists
- ch021: 6/6 complete, output exists
- ch022: 5/5 complete, output exists
- ch023: 5/5 complete, output exists
- current failed blocks: none
- historical failed records: 9
- manual actions needed: none
- next effective action: none
- V3.10 complete: repeatable rollout protocol artifacts exist
- V3.11 complete: report automation command family now exists
- V3.12 complete: glossary and terminology hardening
- V4.0 complete: practical local operator product for the current single-novel workflow
- V4.1 complete: multi-novel foundation now exists through per-project scaffolding and setup/fetch playbooks
- V4.2 complete: structured multi-genre style profiles now exist and are wired into refinement/QA prompts
- V4.3 complete: research-profile workflow now uses `RESEARCH_PROFILE.yaml`, a manual web-research playbook, and prompt context wiring for translation/refinement/QA
- research-profile readiness contract now classifies `pending` / `drafted` / `active`, reports missing fields, and keeps a missing `RESEARCH_PROFILE.yaml` visible without breaking old read-only flows
- `novel-pipeline preflight` now summarizes provider executable availability, workspace/config integrity, research readiness, and git backup guardrails; the operator snapshot mirrors this state
- `novel-pipeline report preflight` now writes a durable diagnostics artifact at `07_Reports/preflight_report.md`
- `novel-pipeline report recovery-drill` now writes a restore-readiness artifact at `07_Reports/recovery_drill.md`
- latest verified preflight state: `ready` on 2026-05-10 after V5.1/V5.2 verification and clean-tree recheck
- V5.0 complete: practical local operator product now covers end-to-end workflow from project scaffold through final-output review
- V5.1 complete: `product-review` report now verifies the product-complete baseline against real run evidence and canonical doc/state checks
- V5.2 complete: canonical root docs are reduced to the three durable source-of-truth files and legacy overlapping root docs are retired
- V5.3 complete: post-complete hardening now includes a generated preflight diagnostics artifact, accepted recovery-drill evidence, operator recovery command hints/quick links, and a canonical recovery checklist template
- V5.4 complete: preflight readiness now ignores churn in known generated report artifacts so report refreshes do not falsely degrade the accepted baseline
- V6.0 complete: operator control dashboard now exposes denser translation control, glossary workbench UX, bounded recovery visibility, and an explicit accepted guardrail panel
- V6.1 complete: system review, naming normalization, archive cleanup, and post-cleanup verification are closed
- V6.2 complete: dashboard UX polish and report-surface separation now keep `07_Reports/` root operational and expose active vs archived report surfaces directly in the operator window
- V6.3 complete: the operator dashboard now uses workflow focus modes and regrouped control panels so the daily translation path is easier to scan without changing bounded execution policy
- V6.4 complete: operator workflow audit and first rebuild landed; the control window is now task-first, removes misleading Primary Actions jump buttons, tags control roles, fixes Run ID layout, and verifies task-tab filtering in browser smoke
- V6.4 audit report exists at `07_Reports/operator_workflow_audit_20260606.md`
- V6.5 complete: operator UI/UX rebuild reduced visible copy, made `Daily Home` the first working surface, moved diagnostics behind `Technical Details`, hid recovery execution when no failures exist, and grouped reports by operator question
- V6.5 audit report exists at `07_Reports/operator_ui_text_surface_audit_20260606.md`
- V4.0 operator window now exists:
  - `novel-pipeline operator [--run-id <run_id>] [--host <host>] [--port <port>] [--open-browser]`
  - local operator window for status, blocker, next safe action, block inspection, glossary queue view, glossary suggestion/decision flow, report generation, artifact viewing, novel-project scaffold, and bounded batch-start actions
  - bounded resume action that requires `until_chapter` or `until_block` and always uses `manual_action_mode=stop`
  - rerun-block action for targeted recovery
  - run-batch action that requires explicit `run_id` and chapter range and supports only scan-only gate or bounded batch mode
  - init-novel action that requires explicit project root, title, and source URL and returns the created profile/config paths
  - glossary approve/reject actions with 2-3 Thai term options now exist
  - glossary approval commits automatically when the queue is cleared
  - broader state-changing controls are still intentionally limited to bounded batch start, bounded recovery, and glossary approval
- V4.1 scaffolding now exists:
  - `novel-pipeline init-novel --project-root <path> --title <title> --source-url <toc_url> ...`
  - per-project `NOVEL_PROFILE.yaml`
  - copied `.system/`, `prompts/`, and `00_Templates/` baseline for a new project
  - isolated per-project `01_Glossary/`, `03_Raw/`, `04_Work/`, `05_Output/`, `06_Logs/`, and `07_Reports/`
  - codex fallback `--cd` is rewritten to the new project root during scaffold
- V4.2 style profile baseline now exists:
  - `.system/style_profiles.yaml` now includes practical presets for `dark_fantasy`, `xianxia_wuxia`, `modern_urban`, `sci_fi`, `horror`, `romance_drama`, and `deep_sea_embers`
  - `StyleProfile` now carries structured fields for tone, naming notes, narration density, glossary categories, and QA criteria
  - refinement and QA prompts now consume structured `style_instructions` instead of hardcoded Deep Sea Embers wording
  - `init-novel` now resolves style selection by explicit `--style-profile`, then normalized `--genre`, then template default
- V4.3 research-profile baseline now exists:
  - per-project `RESEARCH_PROFILE.yaml` is scaffolded by `init-novel`
  - `RESEARCH_PROFILE_PLAYBOOK.md` defines the manual web research workflow anchored to title plus source URL
  - literal translation, refinement, and QA now receive `research_context` from the saved profile
  - the active Deep Sea Embers workspace now has a tracked `RESEARCH_PROFILE.yaml`
- V4.1 playbooks now exist:
  - `NOVEL_SETUP_PLAYBOOK.md`
  - `FETCH_ADAPTER_PLAYBOOK.md`
- V3.12 read-only tooling now exists:
  - `report glossary-conflicts [--run-id <run_id>]`
  - `report glossary-audit --run-id <run_id>`
- V3.12 per-run guard verification now exists:
  - `report glossary-guard --run-id <run_id>`
- V3.12 approval-stage queue revalidation now strips stale/noisy terms from existing glossary scan artifacts before prompting or writing notes
- V3.12 QA-stage glossary gate now blocks the narrow case where literal translation already used an approved Thai term and refinement removes it
- V3.12 first runtime guard slice now exists in glossary scan:
  - exact quarantine/rejected/deprecated terms are filtered before queue entry
  - exact historical rejected terms from prior glossary approvals are filtered before queue entry
  - narrow approved-term noise like `是失乡号` is filtered
  - substring fragments that never occur standalone in a block are filtered
- `glossary-audit` verified clean for `batch-ch019-ch023-v1`
- `glossary-conflicts` intentionally returns actionable findings for current glossary conflicts/noise and is meant to surface cleanup or guardrail work
- `glossary-guard` now proves the current scan-time guard reduces noisy candidates on real chapters for `batch-ch019-ch023-v1`
- broader approval/translation-stage enforcement is not planned right now; the current scan -> approval -> QA guard chain is the accepted V3.12 baseline
- ch024+: must remain unprocessed
- final outputs for ch019-ch023 exist
- V3.10 protocol artifacts now exist:
  - `00_Templates/Batch-Rollout-Checklist.md`
  - `00_Templates/Worker-Bounded-Batch-Prompt.md`
  - `07_Reports/v3_10_repeatable_rollout_protocol.md`
- V3.11 report artifacts now exist:
  - `07_Reports/checkpoint_batch-ch019-ch023-v1.md`
  - `07_Reports/cleanliness_batch-ch019-ch023-v1_ch019-ch020-ch021-ch022-ch023.md`
  - `07_Reports/provider_usage_batch-ch019-ch023-v1.md`
  - `07_Reports/glossary_decisions_batch-ch019-ch023-v1.md`

## Next Safe Action

Do not start a new Deep Sea Embers translation batch yet. Source currently exists only through `ch023`.

Proceed with protocol/product work:

1. Freeze V3.9 completion evidence:
   `novel-pipeline --config ".system/config.yaml" status --run-id batch-ch019-ch023-v1`
2. Freeze current operator baseline:
   `novel-pipeline --config ".system/config.yaml" preflight`
3. Use the new V3.10 artifacts as the reusable handoff package:
   - `00_Templates/Batch-Rollout-Checklist.md`
   - `00_Templates/Worker-Bounded-Batch-Prompt.md`
   - `07_Reports/v3_10_repeatable_rollout_protocol.md`
4. Keep the accepted V5 baseline green by rerunning `preflight` and `report product-review` before any new backlog item that changes operator behavior or reliability policy.
5. Do not plan `ch024+` translation until new source is available and a fresh fetch/scan decision is made.

V5.0 accepted baseline:

- operator can now scaffold a new novel project without dropping to CLI memory:
  - `project_root`
  - `title`
  - `source_url`
  - optional aliases / genre / adapter / style profile
- operator can now edit the concise research-profile fields without dropping to YAML editing:
  - `title`
  - `aliases`
  - `source_url`
  - `status`
  - `synopsis`
  - `tags`
  - `style_notes`
  - `reader_expectations`
  - `review_summary`
  - `last_reviewed_at`
  - `reviewed_by`
  - `terminology`
  - `reference_links`
  - `notes`
- operator can now initiate a batch range without dropping to CLI memory:
  - glossary scan gate (`glossary-scan`)
  - bounded batch run with research readiness enforced
- this does not remove the explicit-approval rule for starting a new production batch
- practical local product scope is now covered end to end from project scaffold through final-output review
- product review evidence now exists at:
  - `07_Reports/product_review_batch-ch019-ch023-v1.md`

Next milestones after product-complete:

- `V5.1`: complete
- `V5.2`: complete
- `V5.3`: complete
- `V5.4`: complete
- `V6.0`: complete
- accepted V5.3 hardening baseline:
  - `07_Reports/preflight_report.md`
  - `07_Reports/recovery_drill.md`
  - operator recovery command hints and quick links
  - `00_Templates/Recovery-Drill-Checklist.md`
- accepted V5.4 reliability baseline:
  - readiness ignores known generated report churn under `07_Reports/`
  - preflight still degrades on ordinary dirty tracked files
- current delivery milestone:
  - `V6.0 Operator Control Dashboard` complete
  - `V6.0A` complete: the dashboard now has run selector, preflight/provider strip, run overview, chapter matrix, current blocker panel, next safe action visibility, and recent activity log
  - `V6.0B` complete: batch/resume/rerun controls now show exact command previews, scope, and guardrails before execution and echo the command in action results
  - `V6.0C` complete: glossary workbench now shows batch progress, per-term note-history intersections, suggestion context, and selected decision preview in one surface
  - `V6.0D` complete: inspect workbench now shows source-through-formatted artifacts, latest stage state, cleanliness findings, and direct rerun-target preparation
  - `V6.0E` complete: the dashboard now surfaces the accepted bounded-action model directly, including allowed state-changing actions, bounded translation rules, and visible report kinds
  - `V6.1 System Review, Verification, And Cleanup` complete
  - `V6.1A` complete: repo audit captured cleanup candidates and classified the main risks before any destructive changes
  - `V6.1B` complete: canonical naming is now normalized around `IMPLEMENT_PLAN.md` across active code, templates, tests, and canonical docs
  - `V6.1C` complete: benchmark/history artifacts now live under archive paths and benchmark/debug helper scripts no longer crowd the active repo surface
  - `V6.1D` complete: compile/tests/preflight/product-review/recovery-drill were rerun successfully after cleanup
  - after `V6.1`, there is no active delivery milestone until a new backlog item is opened explicitly

## Invariants And Guardrails

Never:

- process ch024+ during `batch-ch019-ch023-v1`
- edit fetched source after fetch unless explicitly repairing a proven corrupted fetch artifact
- delete or rewrite ledger history
- create glossary notes for rejected terms
- force-accept QA hard-fails without explicit user/Codex approval
- commit provider quota/error/meta output as successful content
- trust worker reports without checking artifacts and ledger
- let Elephant or Nemotron perform state-changing operations

Always:

- use UTF-8 for commands and file reads/writes
- keep `06_Logs/run_ledger.jsonl` append-only
- inspect latest block state instead of counting historical failures naively
- verify final outputs for provider/meta leakage, Chinese body text, wrong glossary variants, quote-only lines, and formatting drift
- keep runtime artifacts and source cache out of git unless deliberately changing repository policy

Requires explicit user approval:

- starting a new production batch
- force-accepting a QA hard-fail
- changing provider routing
- modifying source artifacts or final outputs manually
- running state-changing work with a new/untested model

## Operating Commands

Run from project root:

```powershell
cd "D:\Fogust\Workspace\Novel\Deep Sea Embers"
$env:PYTHONIOENCODING='utf-8'
```

Deterministic checks:

```powershell
python -m compileall novel_pipeline
python test_translation.py
```

Current status:

```powershell
novel-pipeline --config ".system/config.yaml" status --run-id batch-ch019-ch023-v1
```

Resume current batch only when approved:

```powershell
novel-pipeline --config ".system/config.yaml" resume --run-id batch-ch019-ch023-v1 --manual-action-mode stop
```

Bounded chapter checkpoint:

```powershell
novel-pipeline --config ".system/config.yaml" resume --run-id batch-ch019-ch023-v1 --until-chapter ch019 --manual-action-mode stop
```

Bounded block checkpoint:

```powershell
novel-pipeline --config ".system/config.yaml" resume --run-id batch-ch019-ch023-v1 --until-block ch019-block-005 --manual-action-mode stop
```

Read-only block inspection:

```powershell
novel-pipeline --config ".system/config.yaml" inspect-block --run-id batch-ch019-ch023-v1 --block-id ch019-block-002
```

Targeted block recovery:

```powershell
novel-pipeline --config ".system/config.yaml" rerun-block --run-id batch-ch019-ch023-v1 --block-id <block-id> --from-stage <stage>
```

Scan-only gate for a new range:

```powershell
novel-pipeline --config ".system/config.yaml" run --range chXXX-chYYY --run-id <run-id> --stop-after glossary-scan
```

## Provider Policy

Current routing:

- Gemini: term extraction and literal translation.
- Claude: term suggestions and primary refinement.
- GPT-5.4 via Codex: first refinement fallback after Claude failure.
- Qwen: second refinement fallback and QA judge.
- Gemini: QA fallback only on provider failure.
- Local Python: formatting, ledger/status/bookkeeping.

Hard rules:

- Do not use Claude for literal translation or QA.
- If Gemini literal translation hits quota/capacity, wait/resume. Do not silently fallback to Claude.
- GPT-5.4 fallback outputs require deterministic validation and Qwen QA before commit.
- Provider quota/error/meta output must never be committed as successful output.
- Gemini has Windows argv command-length preflight protection.
- If QA hard-fail escalates to a manual prompt in noninteractive execution, stop and report.

Worker model restrictions:

- Elephant: banned for state-changing work.
- Nemotron: banned for state-changing work.
- Reason: both produced false completion reports during V3.9 glossary approval attempts.
- They may only be used for read-only drafts/checklists where false completion cannot modify state, and Codex must still verify results.

## Known Risks

- Ledger confusion: append-only history contains old failures even after recovery.
- Claude crash: Windows return code `3221225786`, often empty stderr/stdout.
- Gemini command length: argv transport can hit `command_too_long`, especially as QA fallback.
- QA hard-fail: noninteractive workers can abort with EOF at manual prompt.
- QA warning semantics: deterministic warnings should stay auditable but must not override a Qwen `PASS`; regression tests now cover this.
- Formatting drift: formatting can remove dialogue quote marks after QA passes.
- Mojibake/encoding errors: reports or artifacts can display corrupted Chinese/Thai if encoding is mishandled.
- Worker false completion: unreliable free models may claim state changes that did not occur.
- Documentation overwrite: memory docs were previously shortened/damaged by worker edits before git backup existed.

## Recovery Playbooks

### QA hard-fail

1. Stop the run.
2. Read source, literal, refined, formatted if present, and `*.qa.json`.
3. Identify the exact omission or meaning drift.
4. If Qwen says `PASS` and the only findings are deterministic warnings, treat it as a QA rule semantics issue, not a semantic translation failure.
5. Repair code only when the rule semantics are wrong; otherwise repair the narrowest artifact only if deterministic repair is justified.
6. Rerun from the failed stage, usually `qa`.
7. Verify QA, formatting, ledger, and cleanliness.

### Noninteractive EOF

1. Treat as a manual QA prompt.
2. Do not resume blindly.
3. Inspect the QA artifact and decide repair/retry/skip with Codex/user review.

### Claude crash

1. Retry once if the surrounding state is clean.
2. If repeated, allow GPT-5.4 refinement fallback.
3. Validate GPT output deterministically and through Qwen QA.

### Gemini `command_too_long`

1. Do not change literal translation routing to Claude.
2. Try bounded QA-stage rerun if Qwen primary can succeed.
3. If repeated, stop and report before config changes.

### Formatter quote drift

1. Compare refined and formatted artifacts.
2. Restore only lost punctuation if wording is otherwise correct.
3. Do not change Thai prose unless QA/review requires it.
4. Re-run or re-check cleanliness after repair.

### Damaged memory docs

1. Stop worker activity.
2. Check git status and recent commits.
3. Restore tracked docs from git when possible.
4. Reconstruct only missing current state from reports/ledger.
5. Commit and push the repaired memory docs.

## Decision Log

- 2026-04-17: V3.7 accepted after ch004-ch008 production dry run and spot-check.
- 2026-04-18: GPT-5.4 via Codex approved as first refinement fallback after benchmark and bounded recovery results.
- 2026-04-18: V3.8 accepted after ch009-ch018 completion and deterministic checks.
- 2026-04-19: Elephant and Nemotron banned from state-changing work after false completion reports.
- 2026-04-19: GitHub backup repository established at `https://github.com/Tusgof/Novel` to protect memory docs and source.
- 2026-04-20: `PROJECT_BRAIN.md` restructured as project constitution, architecture map, current state, guardrails, and recovery memory.
- 2026-04-20: Runtime safety controls implemented in `f2143f6`: manual-action stop mode, bounded resume, read-only inspect-block, effective status fields, and basic post-format validation.
- 2026-04-23: V3.9 progressed through ch021. Fixed QA warning semantics so deterministic warnings such as `sentence_drop` remain visible but do not block a Qwen `PASS`; ch019-ch021 outputs now exist and pass deterministic cleanliness checks.
- 2026-04-24: V3.9 completed through ch023. A `command_too_long` failure on `ch022-block-004` was recovered by bounded QA-stage rerun; final outputs for ch019-ch023 now exist, deterministic checks pass, and spot-check report was created.
- 2026-04-24: V3.10 accepted. Reusable bounded-batch protocol artifacts were added: checklist template, worker prompt template, and rollout protocol report.
- 2026-04-28: V4.0 accepted. The local operator window now covers status, glossary decision flow, bounded resume, rerun-block, reports, and artifact viewing for the practical single-novel workflow.
- 2026-04-29: V4.2 accepted. Structured multi-genre style profiles now exist, `init-novel` can resolve genre presets to style profile keys, and refinement/QA prompts now consume consistent style instructions without hardcoded Deep Sea Embers wording.
- 2026-04-29: V4.3 accepted. Research is now stored in `RESEARCH_PROFILE.yaml`, collected through a practical web-research playbook, and passed into translation/refinement/QA prompts as concise context.
- 2026-05-10: V5.3 accepted. Post-complete hardening now has a generated preflight diagnostics artifact, accepted recovery-drill evidence, operator recovery hints/quick links, and a canonical recovery checklist without expanding product scope.
- 2026-05-10: V5.4 accepted. Generated report refreshes no longer cause false dirty-tree degradation in preflight/product-review, while ordinary tracked-file drift still degrades readiness as intended.
- 2026-05-11: V6.2 accepted. Historical run evidence moved under `07_Reports/archive/history/`, the root report surface now contains operational baselines only, and the dashboard now renders active report workspace and archive context separately.
- 2026-05-16: V6.3 accepted. The operator dashboard now groups controls by real workflow (`Current Run`, `Glossary`, `Recovery`, `Reports`, `Setup`) and moves setup/report tooling out of the main daily translation path.
- 2026-06-06: V6.4 accepted. Runtime evidence showed backend APIs and guardrails worked while the window failed as a normal-user control surface. The rebuild removed misleading navigation-as-action controls, fixed rendered JS/layout issues, and verified task-first flows: `Continue Translation`, `Glossary Review`, `Recover Block`, `Reports`, and `Project Setup`.
- 2026-06-06: V6.5 accepted. The operator window now prioritizes a concise daily home, hides technical diagnostics by default, suppresses recovery execution controls when there is no failed/manual block, and groups reports by operator question rather than raw report names.

## Document Map

- Canonical memory:
  - `PROJECT_BRAIN.md`
  - `IMPLEMENT_PLAN.md`
  - `OPERATOR_MANUAL.md`
- Playbooks and templates:
  - `NOVEL_SETUP_PLAYBOOK.md`
  - `FETCH_ADAPTER_PLAYBOOK.md`
  - `RESEARCH_PROFILE_PLAYBOOK.md`
  - `00_Templates/Batch-Rollout-Checklist.md`
  - `00_Templates/Worker-Bounded-Batch-Prompt.md`
  - `00_Templates/Novel-Profile.yaml`
  - `00_Templates/Research-Profile.yaml`
- Runtime and policy:
  - `.system/config.yaml`
  - `.system/style_profiles.yaml`
  - `.system/providers.yaml`
  - `D:\Fogust\Workspace\Novel\AGENTS.md`
- Historical evidence:
  - active operational reports remain in `07_Reports/`
  - archived history and benchmarks now live in `07_Reports/archive/`
  - archived run evidence is being tightened under `07_Reports/archive/history/` so the root report surface stays operational

## Roles

- User: product owner, glossary/semantic decision maker, approval authority for risky actions.
- Codex: architect, orchestrator, reviewer, project memory owner, prompt writer, disk-state verifier.
- Worker models: bounded implementers/operators only.
- Providers: translation/refinement/QA engines, never source-of-truth authorities.

## Git Backup

- GitHub repo: `https://github.com/Tusgof/Novel`
- Local repo root: `D:\Fogust\Workspace\Novel\Deep Sea Embers`
- Branch: `main`
- Known pushed commits:
  - `f665df2 Initial novel pipeline safety snapshot`
  - `9a0997b Document GitHub backup repository`
  - `eeec25b Restructure project brain memory`
  - `f2143f6 Add bounded resume safety controls`
- Runtime/production artifact directories are intentionally ignored:
  - `03_Raw/`
  - `04_Work/`
  - `05_Output/`
  - `06_Logs/`
- Tracked source-of-truth includes docs, pipeline code, prompts/config/style profiles, glossary notes, reports/scripts/skills/tests.

## Important Reports

V3.7:

- `07_Reports/archive/history/v3_7/production_dry_run_batch_ch004_ch008_v2.md`
- `07_Reports/archive/history/v3_7/spot_check_batch_ch004_ch008_v2.md`

V3.8:

- `07_Reports/archive/history/v3_8/glossary_scan_batch-ch009-ch018-v1.md`
- `07_Reports/archive/history/v3_8/glossary_classification_batch-ch009-ch018-v1.md`
- `07_Reports/archive/history/v3_8/glossary_approval_decisions_batch-ch009-ch018-v1.md`
- `07_Reports/archive/history/v3_8/ch009_failed_block_recovery_gpt54.md`
- `07_Reports/archive/history/v3_8/ch009_block_006_qa_recovery.md`
- `07_Reports/archive/history/v3_8/v3_8_phase3_ch010_ch013_checkpoint.md`
- `07_Reports/archive/history/v3_8/v3_8_phase4_ch014_ch018_checkpoint.md`
- `07_Reports/archive/history/v3_8/spot_check_batch_ch014_ch018_v1.md`

V3.9:

- `07_Reports/archive/history/v3_9/glossary_scan_batch-ch019-ch023-v1.md`
- `07_Reports/archive/history/v3_9/glossary_classification_batch-ch019-ch023-v1.md`
- `07_Reports/archive/history/v3_9/glossary_approval_decisions_batch-ch019-ch023-v1.md`
- `07_Reports/archive/history/v3_9/spot_check_batch_ch019_ch023_v1.md`
