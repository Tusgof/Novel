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
- spot-check report exists at `07_Reports/archive/history/v3_9/spot_check_batch_ch019_ch023_v1.md`

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

Status: complete on 2026-05-11.

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
  - complete on 2026-05-10:
    - glossary queue now shows batch closure progress and per-term history context
    - glossary suggestion view now shows first-seen location, history intersections, and selected decision preview
    - glossary decision results now echo the approved Thai term when applicable

- V6.0D: Block inspection and recovery workbench
  - tighter inspect-block presentation:
    - source/literal/refined/QA/formatted artifact links
    - latest stage state
    - formatting/cleanliness findings
    - direct rerun target selection
  - done when a failed or suspicious block can be diagnosed and recovered from one place
  - complete on 2026-05-10:
    - inspect-block now surfaces source plus all downstream artifact links
    - inspect view now shows latest stage state and cleanliness findings together
    - inspect view can prefill rerun-block targets directly into the recovery controls

- V6.0E: Acceptance and guardrails
  - no new broad state-changing actions beyond bounded scope already accepted
  - all dashboard actions still enforce:
    - explicit run/range/block scope
    - `manual_action_mode=stop`
    - research-readiness gating
    - deterministic verification/report visibility
  - done when the richer dashboard does not weaken the accepted safety model
  - complete on 2026-05-11:
    - operator snapshot now exposes the accepted guardrail contract directly
    - dashboard UI now shows the allowed state-changing actions, bounded translation rules, and visible report kinds in one panel
    - no new unbounded state-changing action was introduced while closing `V6.0`

Acceptance criteria:

- the dashboard exposes the active translation workflow more clearly than the current operator baseline
- glossary approval is handled through a dedicated dashboard workbench with option selection and decision context
- translation/recovery actions remain bounded and auditable
- compile/tests pass
- docs and operator runbook are synced

Accepted because:

- operator snapshot now exposes an explicit bounded-action guardrail model
- the dashboard renders the same guardrail model in the UI
- compile/tests passed after the `V6.0E` changes
- the accepted safety model from `V5.x` remains intact while the denser dashboard controls are visible in one place

Not part of V6.0:

- visual polish for its own sake
- unbounded one-click production runs
- silent force-accept of QA failures
- new provider routing policy
- automated semantic approval without human review

### V6.1: System Review, Verification, And Cleanup

Goal: review the product-complete system as a maintained repo, classify clutter and stale assets, and clean it without damaging canonical memory, runtime evidence, or accepted operator behavior.

Status: complete on 2026-05-11.

Planned slices:

- V6.1A: Audit and classification
  - inspect repo structure, tracked reports, helper scripts, generated caches, and naming inconsistencies
  - classify each candidate as:
    - keep
    - archive
    - retire/delete
    - normalize/rename
  - complete on 2026-05-11:
    - audit evidence captured in `07_Reports/archive/history/v6_1/system_cleanup_audit_20260511.md`
    - high-value findings identified before any destructive cleanup:
      - `07_Reports/` contains a mix of canonical generated baselines and old benchmark/history artifacts
      - `scripts/` contains post-decision benchmark/test helpers that are likely no longer part of normal product operation
      - `__pycache__/` exists locally but is already ignored and should be treated as disposable cache, not repo content
      - `Implement_PLAN.md` vs `IMPLEMENT_PLAN.md` naming is inconsistent across docs and deserves normalization

- V6.1B: Canonical naming and doc path cleanup
  - normalize durable doc references so the canonical filenames are referred to consistently
  - remove or fix stale references that point to retired or mis-cased root docs
  - done when canonical docs have one stable naming contract
  - complete on 2026-05-11:
    - active code, templates, tests, and canonical docs now use `IMPLEMENT_PLAN.md` consistently
    - git-tracked canonical roadmap path is normalized to `IMPLEMENT_PLAN.md`

- V6.1C: Archive and repo-surface cleanup
  - move non-operational benchmark/history artifacts out of the active working surface while keeping evidence restorable
  - remove disposable local caches that should never be treated as durable state
  - avoid touching accepted runtime evidence or canonical reports needed by product review/preflight
  - done when the active repo surface is materially cleaner without losing important audit history
  - complete on 2026-05-11:
    - benchmark and one-off diagnostic reports were moved under `07_Reports/archive/`
    - doc-memory backup artifacts were moved under `07_Reports/archive/history/`
    - benchmark/debug helper scripts were moved under `scripts/archive/benchmarks/`
    - local `__pycache__/` was removed from the active repo surface

- V6.1D: Verification and clean baseline refresh
  - rerun compile/tests/preflight/product-review after cleanup
  - verify that cleanup did not break operator behavior, doc contracts, or report baselines
  - done when the repo is clean, the accepted baseline still passes, and the cleanup report is updated with final decisions
  - complete on 2026-05-11:
    - `python -m compileall novel_pipeline` passed
    - `python test_translation.py` passed
    - `novel-pipeline --config ".system/config.yaml" preflight` returned `ready`
    - `novel-pipeline --config ".system/config.yaml" report recovery-drill` remained `accepted`
    - `novel-pipeline --config ".system/config.yaml" report product-review --run-id batch-ch019-ch023-v1` remained accepted on the cleaned repo surface

Acceptance criteria:

- cleanup decisions are evidence-based, not ad hoc
- canonical docs remain intact and consistent
- accepted runtime/report baselines remain reproducible
- compile/tests/preflight/product-review still pass after cleanup
- no translation/artifact/ledger state is damaged by cleanup work

Status after V6.1:

- `V6.1A` complete
- `V6.1B` complete
- `V6.1C` complete
- `V6.1D` complete
- `V6.2` became the next backlog item and is now complete

### V6.2: Dashboard UX Polish And Report Surface Separation

Goal: make the operator dashboard easier to scan during daily work and make the `07_Reports/` surface clearly distinguish active operational reports from historical evidence.

Status: complete on 2026-05-11.

Planned slices:

- V6.2A: Report surface separation
  - move non-operational historical run reports out of the `07_Reports/` root into archive paths while preserving evidence
  - keep only current operational baselines and reusable operator references at the root
  - done when the root report surface reads as active operational workspace rather than mixed history
  - complete on 2026-05-11:
    - historical run evidence for V3.7, V3.8, V3.9, and V6.1 cleanup moved under `07_Reports/archive/history/`
    - `07_Reports/` root now contains only active operational baselines plus the reusable rollout protocol reference

- V6.2B: Dashboard report workspace
  - expose active generated reports, active reference reports, and archive counts as separate dashboard surfaces
  - show recent archive files without mixing them into the active quick-link flow
  - done when the operator can tell in one scan what is current, what is reusable baseline, and what is historical evidence
  - complete on 2026-05-11:
    - operator snapshot now exposes `report_surfaces`
    - dashboard now renders a dedicated `Report Workspace` panel with separate active and archive sections

- V6.2C: Focused UX polish
  - tighten the report-generation wording and layout so dashboard actions read as operational controls rather than a flat button list
  - keep the existing bounded execution model intact
  - done when the dashboard improves scan speed and orientation without adding new broad actions
  - complete on 2026-05-11:
    - report actions are labeled as active operational generation rather than a generic report bucket
    - archive visibility is now contextual instead of mixed into the everyday quick-link path

Acceptance criteria:

- compile/tests still pass
- report generation and product-review baselines still work
- active report root and archive paths are clearly separated
- dashboard snapshot/UI expose active reports and archived history separately
- no pipeline run, resume, or rerun-block execution is needed for this polish work

Verification completed on 2026-05-11:

- `python -m compileall novel_pipeline` passed
- `python test_translation.py` passed
- operator runtime snapshot showed:
  - `07_Reports/` root reduced to active operational files only
  - `report_surfaces.active` and `report_surfaces.archive` separated correctly
  - `Report Workspace` markup present in the served dashboard HTML

### V6.3: Dashboard Workflow Simplification

Goal: make the operator dashboard easier to use during daily translation work by reorganizing the existing controls around the real workflow instead of a flat pile of panels.

Status: complete on 2026-05-16.

Completed slices:

- V6.3A: Workflow-first focus model
  - sidebar and top-of-page focus switches now filter the dashboard by `Current Run`, `Glossary`, `Recovery`, `Reports`, `Setup`, or `All`
  - operators can reduce visual noise without losing any existing bounded action

- V6.3B: Regrouped operational controls
  - batch start and bounded resume now live together under `Batch Controls`
  - rerun-block and action-result feedback now live together under `Recovery Controls`
  - glossary queue and glossary decision now sit together as the glossary task surface

- V6.3C: Setup moved out of the daily run path
  - `Init Novel Project` and `Research Profile` editing now live under `Project Setup`
  - report generation moved from the sidebar into a dedicated `Report Controls` panel in the main workspace

Acceptance criteria:

- compile/tests still pass
- no new unbounded state-changing actions are introduced
- all previous action IDs and guarded behaviors remain usable
- the dashboard can be filtered to the operator's current task instead of forcing full-page scanning

### V6.4: Operator Workflow Audit And Control Window Rebuild

Goal: stop treating the current operator window as accepted UX and audit the whole workflow from a real user's point of view. The current system has strong backend guardrails, but the control window still does not reliably match how a normal user expects to continue translation work, approve glossary decisions, recover failures, or understand what button to press next.

Status: complete on 2026-06-06.

Implementation closeout:

- audit report created at `07_Reports/operator_workflow_audit_20260606.md`
- misleading `Primary Actions` jump buttons removed from the operator window
- operator window now leads with task modes: `Continue Translation`, `Glossary Review`, `Recover Block`, `Reports`, `Project Setup`, and `All`
- `Task Guide` now explains task state and the next safe action from the loaded run snapshot
- navigation buttons are tagged with `data-task-role="navigation"`
- read-only, state-changing, setup, report, and provider-assisted controls are tagged with explicit `data-action-role` values
- Run ID input/select layout is fixed so both controls are full-width in the sidebar
- browser smoke verified that task tabs filter panels correctly and the page has no new console errors

Problem statement:

- the backend pipeline is usable through CLI, but the operator window is not yet a trustworthy primary control surface
- important actions exist, but the UI does not make the next safe action obvious enough
- several controls look clickable but behave as navigation/filter helpers rather than execution actions
- run selection, batch start, resume, glossary approval, and recovery are still too exposed as implementation details
- the dashboard is still designed around internal panels instead of user tasks
- the system cannot be considered user-friendly until a user can operate common translation flows from the window without asking Codex which command to run

Audit principles:

- inspect real behavior, not just code presence
- verify every button and form against the API/action it is supposed to trigger
- separate navigation controls from state-changing controls visually and behaviorally
- keep all existing bounded execution guardrails
- do not start translation, provider calls, or artifact-changing pipeline work during audit unless a specific controlled test explicitly requires it and is approved
- prefer one clear user path over many equivalent controls

Planned slices:

- V6.4A: Current workflow audit
  - map the real user workflows:
    - continue Deep Sea Embers from the next chapter range
    - start scan-only glossary gate
    - approve/reject glossary candidates
    - start bounded translation after glossary approval
    - inspect and recover a failed block
    - generate reports and understand whether the run is safe
    - create a new novel project and prepare research profile
  - for each workflow record:
    - what the user currently sees
    - what the user needs to decide
    - which controls are confusing or misplaced
    - which CLI command/API call is the real backend action
    - what should be one click, what should require confirmation, and what should be read-only
  - output: `07_Reports/operator_workflow_audit_<date>.md`
  - done when the audit names concrete UX failures with screenshots or served-HTML/API evidence where practical

- V6.4B: Button and API behavior audit
  - verify every dashboard button:
    - focus/navigation buttons
    - load/refresh run buttons
    - batch run button
    - bounded resume button
    - glossary option loading
    - approve/reject glossary decision
    - inspect block
    - rerun-block
    - report generation
    - init novel
    - save research profile
  - classify each button as:
    - navigation-only
    - read-only API
    - state-changing bounded action
    - setup action
  - identify controls that look like state-changing actions but are navigation-only
  - output: button/action matrix in the audit report
  - done when every visible control has a documented expected effect and a test/smoke-check plan

- V6.4C: User-task redesign specification
  - replace the current panel-first dashboard model with task-first flows:
    - `Continue Translation`
    - `Glossary Review`
    - `Recover Block`
    - `Reports`
    - `Project Setup`
  - each task view must show:
    - current state
    - next safe action
    - required inputs
    - exact action that will run
    - result/output after action
    - stop conditions
  - state-changing buttons must use action wording, not vague navigation wording
  - navigation/filter controls must be visually secondary and never look like execution controls
  - done when the target UI spec is specific enough to implement without redesigning during coding

- V6.4D: Implementation backlog from audit
  - score each finding on two axes:
    - ease: 0 hard, 1 medium, 2 easy
    - importance: 0 low, 1 medium, 2 high
  - prioritize findings with high importance first, especially easy/high-impact fixes
  - split implementation into bounded follow-up milestones rather than one broad UI rewrite
  - done when the next implementation milestone has:
    - explicit scope
    - files likely to change
    - tests/smoke checks
    - stop conditions

- V6.4E: Acceptance test plan for the rebuilt control window
  - define a no-provider smoke path for UI behavior wherever possible
  - define a controlled local/dummy project path for setup and report actions
  - define which actions require user approval before live provider/pipeline execution
  - require browser-level checks, not just static HTML string tests
  - done when the acceptance plan can prove that a normal user can complete the core workflow from the window

Stop conditions:

- any proposed audit step would run live translation/provider calls without explicit user approval
- any implementation starts before the audit identifies the actual failure mode
- a dashboard action can mutate state without showing exact scope first
- a UI change weakens bounded execution, research-readiness gating, or glossary approval guardrails
- the audit report cannot map a visible control to a backend action or intentional navigation behavior

Acceptance criteria:

- `IMPLEMENT_PLAN.md` defines the audit/rebuild milestone before more dashboard code is changed
- the audit report exists and identifies concrete control-window failures
- each visible operator action is classified and verified or marked as failing
- the target redesign is task-first, not panel-first
- the follow-up implementation backlog is prioritized by user impact and ease
- compile/tests/preflight remain green after any documentation or audit tooling changes
- operator HTML/JS renders without syntax errors and task navigation works in browser smoke

### V6.5: Operator UI/UX Rebuild For Normal Users

Goal: turn the current task-first operator window into a genuinely usable daily control surface. The next rebuild must reduce visual noise, remove unnecessary explanatory text, and make the correct next action obvious without requiring the user to understand ledger stages, command names, or Codex memory.

Status: complete on 2026-06-06.

Implementation closeout:

- text/surface audit created at `07_Reports/operator_ui_text_surface_audit_20260606.md`
- sidebar copy reduced to run selector and task navigation only
- first working surface is now `Daily Home`, showing current run, blocker, next safe action, and task guidance before detailed panels
- technical status, provider/git guardrails, command hints, and preflight diagnostics moved behind `Technical Details`
- normal recovery execution controls are hidden when there is no failed/manual block
- reports are grouped by operator question: `System Ready?`, `Run Complete?`, `Output Clean?`, `Provider Issue?`, and `Glossary Safe?`
- glossary decision copy now labels provider-assisted suggestion loading before options are requested
- browser smoke on `127.0.0.1:8765` verified default run load, task switching, collapsed technical details, hidden recovery execution, report grouping, and no new console errors

Design thesis:

- the first screen should answer three questions only:
  - What run/project am I working on?
  - Is anything blocking me?
  - What is the next safe action?
- technical detail should be available on demand, not visible by default
- navigation must look like navigation; execution must look like execution
- every primary button must either do one bounded action or clearly open the one form needed for that action
- copy should be utility copy, not documentation embedded into the UI

Non-goals:

- do not redesign provider routing, ledger semantics, glossary policy, or pipeline stages
- do not add new broad/unbounded pipeline actions
- do not add decorative UI, marketing copy, animations, or cosmetic-only polish
- do not hide guardrails; collapse them behind readable summaries and detail toggles
- do not remove CLI authority; the UI is a control surface over the same bounded backend

Copy reduction rules:

- remove repeated helper text when the label already explains the control
- keep section subtitles to one short sentence only when they prevent a real mistake
- move command previews, guardrails, provider notes, and report explanations into expandable details
- replace internal names with user-task labels where possible:
  - `run-batch` -> `Start Batch`
  - `resume` -> `Continue To Boundary`
  - `rerun-block` -> `Recover This Block`
  - `glossary-scan` -> `Scan Terms`
  - `glossary_approved` -> `Glossary Ready`
- keep exact command/API names visible only in preview/detail areas before execution

Layout target:

- left sidebar:
  - project/run selector
  - task navigation only
  - no long explanations
- main header:
  - current run/project
  - blocker state
  - next safe action
- primary workspace:
  - one active task at a time
  - one primary action per task state
  - secondary details collapsed by default
- right/context area or lower detail area:
  - artifacts, command preview, report links, guardrails, and activity log
  - visible only when useful for the selected task

Milestone slices:

- V6.5A: Text And Surface Audit
  - list every visible heading, subtitle, note, button label, placeholder, and empty-state message in `operator_ui.py`
  - classify each item as:
    - keep visible
    - shorten
    - move to details
    - remove
  - identify panels that exist mainly to explain the system rather than help the operator decide
  - done when the rebuild has a concrete deletion/shortening map before code changes

- V6.5B: Daily Translation Home
  - make `Continue Translation` the default working home
  - show current run, completed/pending/failed summary, and next safe action above the fold
  - if the loaded run is complete, show the next practical choice:
    - start a new explicit scan-only range if source exists
    - fetch/source decision required if source does not exist
  - show only the relevant bounded action form:
    - scan terms
    - continue to chapter/block boundary
    - recover failed block
  - done when the user can understand what to do next from the first viewport

- V6.5C: Glossary Review UX
  - collapse glossary progress into a small state summary:
    - pending
    - approved
    - rejected
    - ready/blocked
  - show one selected term at a time with:
    - source term
    - short context
    - 2-3 Thai options
    - approve/reject buttons
  - hide long history/intersection details behind an expandable section
  - label provider-assisted suggestion loading clearly before it is clicked
  - done when glossary approval can be completed without scanning multiple panels

- V6.5D: Recovery UX
  - hide recovery execution controls when no failed/manual block exists
  - when a failed/manual block exists, show it as the primary task
  - prefill run ID, block ID, and recommended stage from inspection/status when possible
  - keep exact rerun command preview before execution
  - done when recovery starts from a visible failed block, not from blank technical fields

- V6.5E: Reports And Setup De-Clutter
  - keep reports grouped by user question:
    - system ready?
    - run complete?
    - output clean?
    - provider/failure issue?
    - glossary safe?
  - move lower-frequency setup fields out of the daily translation view
  - keep Project Setup as a separate task with short steps:
    - create project
    - research profile
    - preflight
    - source/fetch adapter
    - scan terms
  - done when report/setup controls no longer compete with the daily translation path

- V6.5F: Visual Hierarchy And Responsiveness
  - reduce card nesting and thick panel boundaries
  - make primary action visually dominant and secondary actions plainly secondary
  - keep stable widths/heights for run selector, task nav, action buttons, glossary options, and report controls
  - verify text does not overflow buttons, panels, or mobile widths
  - use a restrained palette and avoid adding decorative visual noise
  - done when the page is scannable on desktop and usable on narrower browser widths

- V6.5G: Browser Acceptance Pass
  - run no-provider browser smoke on the local operator window
  - verify:
    - default run loads
    - task navigation works
    - first viewport shows current run, blocker, and next action
    - glossary task can load queue without mutation
    - recovery task hides execution controls when no failed block exists
    - reports task is grouped by user question
    - no console errors
    - no visible `Primary Actions`-style fake action buttons return
  - done when browser evidence proves the window is usable, not just statically rendered

Stop conditions:

- a UI change makes it easier to run an unbounded or wrong-scope action
- a state-changing action lacks an exact scope/command preview
- primary copy grows instead of shrinking
- the first viewport still requires reading multiple explanatory paragraphs
- provider-backed glossary suggestion is not clearly labeled before use
- tests pass but browser interaction fails

Acceptance criteria:

- visible operator copy is shorter and mapped to user tasks
- the default view makes the next safe action obvious
- internal command/stage names are moved to previews/details instead of front-line UI
- each task has one clear primary action for its current state
- recovery and setup no longer distract from normal translation when not needed
- compile/tests pass
- rendered script syntax check passes
- browser smoke passes on the normal local operator port
- no provider calls or live translation actions are used for UI acceptance unless explicitly approved

### V6.6: Novel-Style Employee Dashboard, Hybrid AI Formatting, Status/Loading UX, And Design Guide

Goal: make the dashboard easier to understand by presenting pipeline responsibilities as named novel-style employees, while keeping the actual runtime stages, ledger names, provider routing, and safety gates auditable. This milestone also closes the current formatting mismatch where `.system/providers.yaml` routes `formatting` to Qwen but the runtime still commits every formatting record as `local`.

Status: complete on 2026-06-08.

Implementation closeout:

- display-only employee roster added for `000 Ferryman` through `007 Warden`
- dashboard renders employee cards with role, mapped real work, provider/model route, readiness, latest activity, and chibi spritesheet asset
- dashboard loading/status surface now identifies the responsible employee/action/provider while work is pending
- provider smoke test exists as an explicit user-triggered action and is not part of normal read-only dashboard load
- formatting now uses configured provider routing first, validates provider output against source content, and falls back to local formatting with audit metadata
- `DESIGN.md` created as the dashboard design source of truth

Locked decisions:

- employee model is display/docs alias only in V6.6
- existing stage names remain source of truth in ledger/config/reports
- dashboard may show employee code/name beside stage/provider, but must still show provider/model/stage for auditability
- no employee abstraction is added to runtime execution until a later explicit milestone
- formatting becomes hybrid gated: AI formatter first when configured, deterministic validation always, local formatter as cleanup/fallback
- provider health checks are two-tier:
  - read-only health check from preflight/status/config inspection
  - optional smoke test only when the user explicitly presses a provider-smoke action
- DeepSeek production routing stays unchanged for now; model migration is deferred and must be tested before routing changes
- `DESIGN.md` becomes the dashboard design source of truth

Employee roster:

| code | name | archetype | real role | maps to |
| --- | --- | --- | --- | --- |
| 000 | Ferryman | คนพาข้ามฝั่ง / ผู้นำทางเข้าท่า | setup, fetch, new project entry | `init-novel`, fetch/source adapter, project setup, preflight |
| 001 | Libra | บรรณารักษ์หญิง | glossary librarian | term extraction, term suggestion, glossary queue, approve/reject |
| 002 | Quill | นักจดถ้อยคำ | literal translator | `literal_translation` |
| 003 | Vesper | บรรณาธิการยามค่ำ | refinement editor | `refinement` |
| 004 | Corvus | ผู้ตรวจคำสาบาน | QA judge | `qa_judge` |
| 005 | Loom | ช่างเรียงรูปเล่ม | formatting/layout worker | `formatting` |
| 006 | Archivist | ผู้เฝ้าหอจดหมายเหตุ | reports/output keeper | reports, final output, cleanliness/product review |
| 007 | Warden | ผู้คุมประตูฉุกเฉิน | recovery worker | inspect-block, rerun-block, failed block recovery |

Dashboard employee rules:

- show a card for every employee with code, name, role, mapped real stage/action, provider/model route, readiness, latest run activity, and current loading/action state
- employee cards must describe what the system actually does today; do not invent tasks that are not implemented
- employee art may be chibi/cartoon novel-style assets, but it is decoration around real operational state, not a replacement for audit fields
- if employee labels appear in reports, reports must still include raw provider, model, stage, block ID, run ID, and output path
- employee names should feel like novel characters but remain readable for a normal operator

Implementation slices:

- V6.6A: Employee Layer
  - add a small static roster for display metadata
  - map roster entries to existing stages/actions only
  - surface employee labels in the operator snapshot and dashboard
  - include chibi dashboard asset references without making assets required for pipeline execution
  - done when dashboard can render the eight employee cards and tests prove the roster is display-only

- V6.6B: Employee Status And Loading Dashboard
  - show readiness as `ready`, `warning`, `blocked`, or `unknown`
  - use preflight/status/config inspection for read-only readiness
  - add a loading/status strip that shows current employee, stage/action, provider/model, elapsed time, retry/fallback/waiting state, and last safe UI log line
  - add an explicit optional provider smoke-test control that clearly warns it will call providers
  - done when read-only dashboard load calls no providers and provider smoke requires an explicit user action

- V6.6C: Hybrid AI Formatting
  - use existing `prompts/formatting.md` for provider-backed formatting
  - route formatting through `.system/providers.yaml` when configured
  - preserve dialogue quotes, thought italics, skill brackets, sound-effect styling, and paragraph spacing
  - run deterministic formatted-text validation after provider output and after local fallback
  - keep local formatter available as cleanup/fallback
  - commit formatting ledger provider as the actual successful formatter provider, not always `local`
  - stop if both provider formatting and local fallback fail validation
  - done when formatting tests cover quote preservation, thought/sound-effect layout, provider/meta leakage rejection, Han leakage rejection, and unsafe output blocking

- V6.6D: DeepSeek Compatibility Backlog
  - keep `deepseek-reasoner` in production routing for now
  - test `deepseek-v4-flash` and `deepseek-v4-pro` before `2026-07-24`
  - consider `deepseek-v4-flash` for cheap formatting only after smoke test and one bounded block test
  - consider `deepseek-v4-pro` for QA/reasoning only after confirming thinking support through the Qwen/OpenAI-compatible bridge
  - do not list Elephant or Nemotron as usable production implementers
  - done when the migration note is documented and no production provider routing is changed

- V6.6E: Dashboard Design System
  - create `DESIGN.md`
  - encode Wise-inspired dashboard principles: clear, friendly, restrained, green accent for ready/positive states
  - incorporate the local `ui-ux.txt` rules that matter here: hierarchy, 4/8-point spacing, semantic colors, component states, loading feedback, and immediate system response
  - prioritize function over decoration
  - forbid marketing hero treatment, decorative gradients, and noisy card walls
  - done when dashboard changes can be reviewed against `DESIGN.md`

Stop conditions:

- an employee label hides or replaces raw provider/model/stage audit data
- dashboard read-only load triggers a live provider call
- provider smoke test can run without an explicit user action
- formatting provider output is committed without deterministic validation
- local fallback masks a semantic formatting failure without ledger metadata
- the dashboard becomes more decorative but less useful for continuing a run, approving glossary, recovering a block, or reading the current blocker
- DeepSeek routing is changed without a separate smoke test, bounded block test, and migration report

Acceptance criteria:

- `IMPLEMENT_PLAN.md` includes V6.6 and the employee roster
- `DESIGN.md` exists and is used as the dashboard design reference
- employee status cards render in the dashboard
- employee cards include real role, mapped stage/action, provider/model, readiness, and chibi asset
- read-only status/bootstrap path does not call providers
- optional provider smoke test is explicit and separate from normal dashboard load
- loading state shows employee/stage/provider progress for long actions
- formatting ledger records show the actual successful formatting provider
- deterministic formatted-text validation remains mandatory
- `python -m compileall novel_pipeline` passes
- `python test_translation.py` passes
- `novel-pipeline --config ".system/config.yaml" preflight` passes or reports only accepted warnings
- browser smoke confirms employee cards render and no new console errors appear

### V6.7: DESIGN.md Dashboard Shell Rebuild

Goal: replace the remaining "feature wall" dashboard structure with a simpler operator shell that matches `DESIGN.md`: one clear decision area, one active task workspace, and one compact status rail. This is a UX/layout milestone only; it must not change provider routing, ledger semantics, pipeline stages, or state-changing guardrails.

Status: complete on 2026-06-08.

Implemented:

- the first viewport now starts with `Current decision`, run overview, current blocker, next action, and compact task guidance
- sidebar workflow choices now use normal operator language: `Continue Translation`, `Review Glossary`, `Recover Block`, `Generate Reports`, `Project Setup`, and `All Surfaces`
- the main area is split into:
  - task workspace for bounded translation, glossary review, recovery, setup, and report controls
  - right status rail for employees, manual actions, reports, research readiness, technical details, and activity
- old `Daily Home` / `Employee Status` labels and duplicate hidden task header were removed
- employee cards were compacted so they show real work, provider route, readiness, and latest activity without crowding the active task controls
- technical diagnostics remain available but collapsed behind `Technical Details`
- provider smoke remains explicit and user-triggered only

Acceptance evidence:

- `python -m compileall novel_pipeline` passed
- `python test_translation.py` passed
- `novel-pipeline --config ".system/config.yaml" preflight` ran and reported only the expected dirty-worktree warning while this milestone was being edited
- served dashboard returned HTTP 200 at `http://127.0.0.1:8766/`
- served HTML contains `Current decision`, `Employees`, `right-rail`, and `task-surface`
- served HTML no longer contains old visible labels `Daily Home` or `Employee Status`
- read-only bootstrap for `batch-ch019-ch023-v1` returned employee status, report surfaces, guardrails, and no current failed blocks

Stop conditions:

- any dashboard read-only load calls providers
- any task navigation behaves like a state-changing action
- any state-changing control loses its explicit scope preview
- provider/model/stage audit fields are hidden behind employee labels

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
