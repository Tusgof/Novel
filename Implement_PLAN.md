# Implement Plan

This document is the practical roadmap from the current verified state to a product-complete operator workflow. It is intentionally operational, not historical.

## Project Finish Line

The project is finished when the user can operate a new novel end to end without Codex acting as manual command memory:

- create or configure a novel project
- search and save a concise research profile
- scan glossary candidates
- approve or reject terms safely
- translate bounded batches
- recover failed blocks and checkpoints
- generate and verify reports
- review final outputs from a practical local operator workflow

Finish also requires that worker models cannot silently mutate source-of-truth docs or artifacts, and that Codex remains the architect, reviewer, and verifier rather than the memory layer for routine operations.

## Current Verified State

- V3.7 complete: `ch004-ch008`
- V3.8 complete: `ch009-ch018`
- V3.9 complete: `batch-ch019-ch023-v1`
- `ch019`: 5/5 blocks complete, `05_Output/ch019/ch019.md` exists
- `ch020`: 5/5 blocks complete, `05_Output/ch020/ch020.md` exists
- `ch021`: 6/6 blocks complete, `05_Output/ch021/ch021.md` exists
- `ch022`: 5/5 blocks complete, `05_Output/ch022/ch022.md` exists
- `ch023`: 5/5 blocks complete, `05_Output/ch023/ch023.md` exists
- current active translation batch: none
- V3.10 complete: repeatable rollout protocol artifacts created
- V3.11 complete: report automation command family created
- V3.12 complete: glossary hardening report layer, runtime scan guards, approval-stage queue revalidation, historical rejected-term guard, narrow QA glossary enforcement, and per-run guard verification implemented
- V4.0 complete: local operator window now covers status, glossary decisions, bounded recovery controls, reports, and artifact viewing
- V4.1 complete: multi-novel foundation now includes `init-novel` scaffolding, `NOVEL_PROFILE.yaml`, and setup/fetch playbooks
- V4.2 complete: multi-genre style profiles now exist and are wired into refinement/QA prompts
- V4.3 complete: research-profile workflow now uses `RESEARCH_PROFILE.yaml`, a manual web-research playbook, and prompt context wiring for translation/refinement/QA
- current failed blocks: none
- historical failed records exist because the ledger is append-only
- source currently exists only through `ch023` in workspace, so future Deep Sea Embers ranges require fetch/scan decisions first
- approved terms:
  - `实太阳神` -> `สุริยเทพที่แท้จริง`
  - `面具神` -> `เทพหน้ากาก`

## Working Model

- Codex plans each milestone and writes the worker prompt.
- `GPT-5.4-mini` medium implements only the assigned bounded scope.
- Codex verifies disk state, tests, reports, and `git diff`.
- Codex loops feedback until acceptance criteria pass.
- Worker reports are claims until verified against real files and deterministic output.

## Milestone Roadmap

### V3.9: Finish `ch019-ch023` Safely

Goal: complete the current batch without losing control of the run or processing outside the intended range.

- V3.9A: bounded `ch019` completion from `ch019-block-003` - done
- V3.9B: `ch019` output gate - done
- V3.9C: bounded `ch020-ch023` translation - done
- V3.9D: final deterministic checks, spot-check report, doc sync - done

Stop on any of the following:

- manual QA prompt
- provider failure
- `command_too_long`
- format validation failure
- any `ch024+` activity

Done when:

- outputs `ch019-ch023` exist
- no current failed blocks remain
- no `ch024+` records exist for the run
- reports are created

Completion evidence:

```powershell
novel-pipeline --config ".system/config.yaml" status --run-id batch-ch019-ch023-v1
```

Expected verified state:

- `26/26` blocks complete
- `05_Output/ch019` through `05_Output/ch023` exist
- current failed blocks: none
- manual actions needed: none
- spot-check report exists at `07_Reports/spot_check_batch_ch019_ch023_v1.md`

### V3.10: Repeatable Rollout Protocol

Goal: make bounded batch handoff repeatable without rewriting the process each time.

Deliverables:

- `00_Templates/Batch-Rollout-Checklist.md`
- `00_Templates/Worker-Bounded-Batch-Prompt.md`
- `07_Reports/v3_10_repeatable_rollout_protocol.md`

Status: done on 2026-04-24 because the reusable checklist, worker prompt template, and practical protocol now exist and define the bounded handoff process.

Acceptance: Codex can hand one bounded batch prompt to a worker using the reusable artifacts without rewriting the process. No new translation batch is required for this milestone.

### V3.11: Report and Verification Automation

Goal: turn recurring verification work into generated artifacts instead of manual prose reconstruction.

- automatic checkpoint report generator
- final-output cleanliness report
- provider usage/failure report
- glossary decision report template

Status: complete on 2026-04-28.

Implemented:

- `novel-pipeline report checkpoint --run-id <run_id> [--output <path>]`
- `novel-pipeline report cleanliness --run-id <run_id> [--chapter-id <chXXX>] [--output <path>]`
- `novel-pipeline report provider-usage --run-id <run_id> [--output <path>]`
- `novel-pipeline report glossary-decisions --run-id <run_id> [--output <path>]`
- generated artifacts verified on `batch-ch019-ch023-v1`:
  - `07_Reports/checkpoint_batch-ch019-ch023-v1.md`
  - `07_Reports/cleanliness_batch-ch019-ch023-v1_ch019-ch020-ch021-ch022-ch023.md`
- `07_Reports/provider_usage_batch-ch019-ch023-v1.md`
- `07_Reports/glossary_decisions_batch-ch019-ch023-v1.md`

Done when the recurring verification reports used in normal operation are generated by commands or scripts, not manual reconstruction.

### V3.12: Glossary and Terminology Hardening

Goal: reduce glossary risk before it reaches translation and QA.

- richer glossary conflict detector
- substring, quarantine, and approved-overlap detection
- rejected-term guard
- per-chapter glossary usage audit

Status: complete on 2026-04-28.

Implemented:

- `novel-pipeline report glossary-conflicts [--run-id <run_id>]`
- `novel-pipeline report glossary-audit --run-id <run_id>`
- `novel-pipeline report glossary-guard --run-id <run_id> [--output <path>]`
- approval-stage queue revalidation now filters stale/noisy terms from older glossary scan artifacts before prompting or writing glossary notes
- QA-stage glossary gate now blocks only when an approved source-side glossary surface survives in refined output without its Thai term
- deterministic scan-time guard now filters:
  - exact quarantine/rejected/deprecated terms and aliases
  - exact historical rejected terms from prior completed glossary approvals
  - narrow noisy prefix/suffix wrappers around approved terms such as `是失乡号`
  - substring fragments that never occur standalone within the block text
- verified against `batch-ch019-ch023-v1`:
  - `07_Reports/glossary_conflicts_batch-ch019-ch023-v1.md`
  - `07_Reports/glossary_audit_batch-ch019-ch023-v1.md`
  - `07_Reports/glossary_guard_batch-ch019-ch023-v1.md`

Done when glossary approval is less dependent on manual ad hoc review.

### V4.0: Practical Local Operator Product

Goal: give the user a local operator window that supports the real workflow without adding cosmetic noise.

- local operator window focused on function, not beauty
- show run status, current blocker, next safe command, block inspection, glossary candidates
- approve/reject UI
- select one Thai term from 2-3 options
- support bounded resume, rerun-block, report generation, artifact opening

Current slice:

- `novel-pipeline operator [--run-id <run_id>] [--host <host>] [--port <port>] [--open-browser]`
- local HTTP operator window using existing pipeline/report functions
- implemented:
  - run status dashboard
  - current blocker / next effective action
  - chapter progress table
  - block inspection with artifact links and formatting validation issues
  - glossary candidate queue view after current deterministic revalidation
  - provider-backed glossary suggestion view with 2-3 Thai options per term
  - approve/reject glossary decisions from the operator window
  - automatic `glossary_approved` commit when the effective queue is empty
  - report generation buttons for existing `report` command family
  - artifact viewer for workspace files
  - bounded resume control that always runs with `manual_action_mode=stop`
  - rerun-block control for targeted recovery
- intentionally not implemented yet:
  - broader state-changing controls beyond glossary approval plus bounded resume/rerun-block

Status: complete on 2026-04-28.

Done because the operator can now handle the practical single-novel workflow without requiring Codex to remember commands:

- inspect status and blockers
- inspect block artifacts
- generate reports
- review glossary candidates
- load Thai term options
- approve or reject glossary terms
- commit glossary approval when queue is clear
- run bounded resume checkpoints
- rerun a failed block from a chosen stage

### V4.1: Multi-Novel Foundation

Goal: let the pipeline support a second novel without code edits.

- per-novel project profile
- isolated vault, artifact, and output paths
- glossary namespace per novel
- source adapter config per novel
- run IDs and reports scoped by novel

Status: complete on 2026-04-29.

Implemented:

- `novel-pipeline init-novel --project-root <path> --title <title> --source-url <toc_url> ...`
- per-novel `NOVEL_PROFILE.yaml` scaffold with:
  - title
  - aliases
  - source/target languages
  - genre
  - style profile
  - source adapter
  - source TOC URL
  - research placeholder fields
- project scaffolding copies the working `.system/providers.yaml`, `.system/style_profiles.yaml`, `prompts/`, and `00_Templates/`
- codex provider `--cd` path is rewritten to the new project root during scaffold so fallback runs stay project-scoped
- isolated per-project folders are created for glossary, raw, work, output, logs, reports, and skills
- setup artifacts added:
  - `00_Templates/Novel-Profile.yaml`
  - `NOVEL_SETUP_PLAYBOOK.md`
  - `FETCH_ADAPTER_PLAYBOOK.md`

Done because a second novel can now be configured from the current workspace without code edits, and the setup/fetch path is documented as a repeatable operator playbook.

### V4.2: Multi-Genre Style Profiles

Goal: make style selection explicit and reusable across genres.

- genre presets: dark fantasy, xianxia/wuxia, modern urban, sci-fi, horror, romance/drama
- controls for tone, naming, narration density, glossary categories, QA criteria

Status: complete on 2026-04-29.

Implemented:

- structured `StyleProfile` fields now include:
  - `genre_label`
  - `tone`
  - `naming_notes`
  - `narration_density`
  - `glossary_categories`
  - `qa_criteria`
- `.system/style_profiles.yaml` now provides practical presets for:
  - `default`
  - `dark_fantasy`
  - `xianxia_wuxia`
  - `modern_urban`
  - `sci_fi`
  - `horror`
  - `romance_drama`
  - `deep_sea_embers`
- refinement and QA prompts now consume structured `style_instructions` instead of hardcoded Deep Sea Embers wording
- `init-novel` now resolves the style profile in this order:
  - explicit `--style-profile`
  - normalized `--genre` mapped to a known preset
  - fallback to the template config default

Done because a new project can now choose a standard genre preset or point to a specific style profile key, and the selected style instructions are used consistently in refinement and QA prompts.

### V4.3: Novel Research Profile

Goal: reduce dependence on one chapter as style evidence.

- setup workflow searches web for synopsis, tags, reviews, style discussion, reader expectations
- save concise research profile
- profile feeds translation, refinement, and QA prompts

Status: complete on 2026-04-29.

Implemented:

- per-project `RESEARCH_PROFILE.yaml` is now a first-class scaffold artifact created by `init-novel`
- `00_Templates/Research-Profile.yaml` now defines a concise schema for:
  - title and aliases
  - source URL
  - synopsis
  - tags
  - style notes
  - reader expectations
  - review summary
  - terminology
  - reference links
- `RESEARCH_PROFILE_PLAYBOOK.md` now defines the step-by-step web research workflow using title plus source URL as the setup anchor
- the active Deep Sea Embers workspace now has a verified `RESEARCH_PROFILE.yaml`
- `AppConfig` now loads optional research context from `RESEARCH_PROFILE.yaml`
- literal translation, refinement, and QA prompts now receive `research_context`
- `NOVEL_PROFILE.yaml` now points to `RESEARCH_PROFILE.yaml` instead of carrying a stale inline research blob

Done because new novel setup no longer depends on one chapter as style evidence alone: it now has a dedicated research artifact, a practical web-research workflow, and prompt wiring that consumes the saved profile.

### V4.4: Packaging and Operator Reliability

Goal: make the tool restorable and movable without tribal knowledge.

- install/setup validation
- environment checks for provider CLIs
- config validation
- backup and git guardrails
- research-profile readiness contract: `pending` / `drafted` / `active`, required-field checks, missing-field reporting, and nonblocking missing-profile visibility

Status: complete. `novel-pipeline preflight` now checks provider executables, config/workspace integrity, research-profile readiness, and git backup guardrails; the operator snapshot surfaces the same preflight state.

Done when the tool can be restored or moved without rebuilding tribal knowledge.

### V5.0: Product Complete Gate

Goal: make the workflow self-sufficient for normal novel production.

- user can create a new novel project, research it, scan glossary, approve terms, translate bounded batches, recover failures, generate reports, and review final outputs from operator workflow
- worker models cannot silently mutate source-of-truth docs or artifacts
- Codex remains architect/reviewer, not manual command memory layer

Status: complete. The local operator workflow now covers new-project scaffold, concise research-profile authoring, glossary scan/approval, bounded batch start, bounded resume/rerun recovery, report generation, artifact inspection, and final-output review from the same control surface.

Current progress:

- operator workflow can now scaffold a new novel project through `init-novel` inputs and return the created profile/research/config paths
- operator workflow can now view and save concise `RESEARCH_PROFILE.yaml` fields without dropping to manual YAML editing:
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
- operator workflow can now start a batch range in two guarded modes:
  - scan-only gate via `stop_after=glossary-scan`
  - bounded batch run with research-readiness enforcement
- operator batch actions still require explicit `run_id`, explicit chapter range, and always use `manual_action_mode=stop`

Done because the workflow can now operate end to end with bounded human decision points and safe recovery for the practical local product scope.

### V5.1: Product-Complete Review And Verification

Goal: verify that V5.0 is genuinely complete in practice, not just feature-complete on paper.

Status: complete on 2026-05-10.

- run a strict acceptance review against the canonical operator flow:
  - init novel
  - fill concise research profile
  - run scan-only glossary gate
  - approve glossary terms
  - run bounded translation
  - recover a bounded failure path
  - generate reports
  - inspect final outputs
- verify that the flow works from operator/CLI surfaces without relying on undocumented Codex memory
- verify that preflight, readiness gating, and bounded-stop guardrails behave as documented
- verify that git state, docs, and runtime evidence stay coherent

Stop when:

- acceptance evidence is missing
- operator flow requires undocumented manual steps
- guardrails fail to stop unsafe execution
- worker claims do not match disk state

Done when:

- a review/verification report exists
- the operator flow is demonstrated end to end against the accepted product scope
- any gaps are either fixed or recorded as explicit post-complete backlog

Implemented:

- `novel-pipeline report product-review --run-id <run_id> [--output <path>]`
- `07_Reports/product_review_batch-ch019-ch023-v1.md`
- deterministic review now verifies:
  - preflight state
  - canonical root docs present and retired root docs absent
  - required operator/playbook/template files present
  - final outputs exist and pass cleanliness checks
  - glossary approval evidence exists
  - recovery evidence exists without current failed blocks

Accepted because:

- `python -m compileall novel_pipeline` passes
- `python test_translation.py` passes
- `novel-pipeline --config ".system/config.yaml" report product-review --run-id batch-ch019-ch023-v1` produces an accepted review on a clean tree
- `novel-pipeline --config ".system/config.yaml" preflight` returns `ready` after the V5.1/V5.2 sync commit

### V5.2: Canonical Docs And Memory Cleanup

Goal: reduce memory sprawl so the project has one clear document set instead of overlapping historical plans.

Status: complete on 2026-05-10.

- define the canonical root doc set
- consolidate still-useful legacy doc content into `PROJECT_BRAIN.md`
- retire obsolete root docs that duplicate canonical memory
- preserve reports/playbooks/templates that remain operational inputs

Stop when:

- a legacy doc is still referenced by active workflow after retirement
- canonical ownership of a topic is ambiguous

Done when:

- `PROJECT_BRAIN.md` holds the important durable project memory
- `IMPLEMENT_PLAN.md` is only the roadmap
- `OPERATOR_MANUAL.md` is only the runbook
- obsolete overlapping root docs are removed or explicitly retired

Accepted because:

- canonical root docs are now limited to:
  - `PROJECT_BRAIN.md`
  - `IMPLEMENT_PLAN.md`
  - `OPERATOR_MANUAL.md`
- operational supporting docs remain explicit:
  - playbooks
  - templates
  - generated reports
- retired root docs are absent:
  - `MASTER_PLAN.md`
  - `REPORT.md`
  - `SUMMARY.md`
- `product-review` verification now checks this doc contract directly

### V5.3: Post-Complete Hardening And Polish

Goal: improve reliability and operator efficiency after the product-complete baseline is verified.

Status: complete on 2026-05-10.

- acceptance-driven UX cleanup
- restore/recovery drills
- tighter environment diagnostics
- small operator friction reductions that do not expand scope
- packaging polish only after review/verification is closed

Implemented:

- `novel-pipeline report preflight [--output <path>]` now generates a durable diagnostics artifact for the current workspace without requiring a run ID
- operator report actions now include `preflight`
- operator preflight panel now shows:
  - workspace/config paths
  - research readiness state
  - per-provider status, stages, transport, and resolved executable path
  - git branch/head/origin/working-tree state
- `novel-pipeline report recovery-drill [--output <path>]` now verifies recovery preconditions for the canonical docs and runtime ignore policy
- operator report actions now include `recovery-drill`
- recovery drill currently checks:
  - repo is inside a git work tree
  - remote `origin` exists
  - canonical docs are tracked and restorable from `HEAD`
  - runtime directories (`03_Raw`, `04_Work`, `05_Output`, `06_Logs`) remain ignored and untracked
- operator bootstrap snapshot now includes:
  - copyable command hints for preflight, reports, status, and first-failed-block inspection
  - quick links to canonical docs and high-value reports when those files exist
- `00_Templates/Recovery-Drill-Checklist.md` now defines the exact restore sequence for canonical docs without mixing runtime artifact recovery into git-based recovery

These slices are not product-scope expansion. They are post-complete diagnostics and recovery hardening so the operator can inspect environment state, capture evidence, and prove that canonical memory can be restored safely without pulling runtime state into git.

Accepted because:

- `novel-pipeline --config ".system/config.yaml" preflight` returns `ready`
- `novel-pipeline --config ".system/config.yaml" report preflight` generates `07_Reports/preflight_report.md`
- `novel-pipeline --config ".system/config.yaml" report recovery-drill` generates `07_Reports/recovery_drill.md` with accepted recovery baseline
- `novel-pipeline --config ".system/config.yaml" report product-review --run-id batch-ch019-ch023-v1` returns accepted on a clean tree after the hardening slices land
- operator recovery hints and quick links now expose the exact commands and canonical files needed for bounded inspection and restore

After V5.3 there is no active delivery milestone. Future work should be opened as explicit backlog items rather than reopening product-complete scope implicitly.

### V5.4: Generated Report Baseline Hygiene

Goal: keep readiness and product-review checks trustworthy even when the operator regenerates tracked report artifacts.

Status: complete on 2026-05-10.

Implemented:

- preflight git cleanliness now ignores changes to known generated report artifacts under `07_Reports/` when deciding readiness
- ignored generated report paths are surfaced explicitly in the preflight summary/report instead of silently disappearing
- `product-review` can now remain accepted after `report preflight` or other generated-report refresh steps, provided no non-report tracked files are dirty

Accepted because:

- `build_preflight_summary(...)` still degrades on ordinary dirty tracked files
- generated changes to known report outputs no longer force a false dirty-tree warning by themselves
- the `V5.3` closeout sequence can regenerate `preflight_report.md` and keep `product_review_*.md` accepted on a clean source tree

After V5.4 there is no active delivery milestone. Future work should still be opened as explicit backlog items.

### V6.0: Operator Control Dashboard

Goal: turn the current functional operator window into a denser control dashboard for daily translation operations, without widening execution risk.

Status: active on 2026-05-10.

Why this is separate from V4.0/V5.0:

- the current operator already supports glossary approval, bounded batch start, bounded resume, rerun-block, reports, artifact viewing, and research-profile editing
- what is missing is a more unified control surface for active translation work, chapter progress, failure handling, and glossary decision flow
- this is a usability and operational-density milestone, not a product-scope reset

Planned slices:

- V6.0A: Dashboard density and control layout
  - single-page run dashboard with:
    - run selector
    - chapter progress matrix
    - current blocker panel
    - next safe action panel
    - provider/preflight strip
    - recent action/result log
  - done when the operator can understand current run state without jumping across multiple panels
  - complete on 2026-05-10.
  - first implementation round landed on 2026-05-10:
    - run selector wired from known ledger run IDs
    - chapter progress matrix added above the detailed chapter table
    - preflight/provider status strip added
    - current blocker panel added
    - recent activity log added for snapshot/report/inspect/action events
  - closing round landed on 2026-05-10:
    - run overview panel now collocates scope, blocker, next safe action, and chapter pressure
    - run subtitle now summarizes scope, output coverage, and current failed blocks
    - chapter matrix is sorted by pressure and shows next pending block/stage

- V6.0B: Translation control actions
  - clearer start/stop/resume/recovery controls for:
    - scan-only gate
    - bounded batch run
    - bounded resume to chapter/block
    - rerun-block from explicit stage
  - stronger action confirmation text showing exact command equivalence and exact scope
  - done when translation control actions are visible and auditable from the dashboard without ambiguous scope
  - complete on 2026-05-10:
    - batch, resume, and rerun controls now render exact CLI-equivalent previews before execution
    - each state-changing control now shows scope and guardrail text inline
    - action result now echoes the previewed command for auditability after execution

- V6.0C: Glossary approval workbench
  - richer glossary queue panel with:
    - source term
    - suggested Thai options
    - selected decision preview
    - note/status context if the term intersects approved/rejected/quarantine history
    - batch-level progress for glossary approval closure
  - done when glossary approval can be handled from one dedicated workbench instead of scattered UI fragments

- V6.0D: Block inspection and recovery workbench
  - tighter inspect-block presentation:
    - source/literal/refined/QA/formatted artifact links
    - latest stage state
    - formatting/cleanliness findings
    - direct rerun target selection
  - done when a failed or suspicious block can be diagnosed and recovered from one place

- V6.0E: Acceptance and guardrails
  - no new broad state-changing actions beyond bounded scope already accepted
  - all dashboard actions still enforce:
    - explicit run/range/block scope
    - `manual_action_mode=stop`
    - research-readiness gating
    - deterministic verification/report visibility
  - done when the richer dashboard does not weaken the accepted safety model

Acceptance criteria:

- the dashboard exposes the active translation workflow more clearly than the current operator baseline
- glossary approval is handled through a dedicated dashboard workbench with option selection and decision context
- translation/recovery actions remain bounded and auditable
- compile/tests pass
- docs and operator runbook are synced

Not part of V6.0:

- visual polish for its own sake
- unbounded one-click production runs
- silent force-accept of QA failures
- new provider routing policy
- automated semantic approval without human review

## Acceptance Gates

This document rewrite is accepted only when:

- `IMPLEMENT_PLAN.md` is updated together with the three V3.10 protocol artifacts and the related operator memory docs
- the file is valid UTF-8
- the required exact terms are present
- the new structure matches this roadmap, not the old plan
- no provider calls were made during the rewrite
- no pipeline run, resume, or rerun-block was executed during the rewrite

Future work gates:

- each milestone must have a clear stop condition
- each worker task must be bounded to a specific range or artifact set
- every claimed completion must be verified against disk state, report files, and `git diff`
- no milestone can be marked done from a worker report alone
- deterministic QA warnings may remain visible without blocking a Qwen `PASS`; deterministic errors and AI judge failure findings still block

## Deferred / Not Now

- UI polish beyond functional clarity
- speculative API/interface claims
- rewriting `PROJECT_BRAIN.md` inside this task
- editing source, config, glossary, reports, ledger, or artifacts as part of this documentation rewrite
- claiming any chapter beyond `ch023` is complete
- adding support for unverified future ranges before fetch/scan decisions are made

## Operating Rules For Future Work

- Do not run provider calls during documentation edits.
- Do not run `resume`, `run`, or `rerun-block` as part of a plan rewrite.
- Treat this file as roadmap only; it does not authorize execution.
- Keep future milestones bounded and explicit.
- Verify output files and ledger state before accepting any worker claim.
- Do not silently fall back to a different provider when a required provider path is part of the active policy.
- Do not expand scope from the current verified range without an explicit fetch/scan decision.
- Keep future operator tools practical first: status, blocker, next safe command, bounded recovery, and report generation.
- If a QA artifact has Qwen `PASS` plus warning-only deterministic findings, keep the warning auditable and continue; if there is any AI judge failure or deterministic error, stop for repair or review.
