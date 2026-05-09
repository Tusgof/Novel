# Project Brain: Deep Sea Embers Translation Pipeline

Last updated: 2026-04-29
Last verified: 2026-04-29 after V4.3 was completed and verified with `python -m compileall novel_pipeline` and `python test_translation.py`.

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
- `07_Reports/`: scan, classification, approval, checkpoint, benchmark, and spot-check reports.

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
- latest verified preflight state: `ready` on 2026-04-29 (`main`, head `60bfc0f`, working tree clean, research status `active / ready`)
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
4. Start `V5.0` from this stable multi-novel, multi-genre, research-profile, and preflight baseline.
5. Do not plan `ch024+` translation until new source is available and a fresh fetch/scan decision is made.

Current V5.0 slice in progress:

- operator can now scaffold a new novel project without dropping to CLI memory:
  - `project_root`
  - `title`
  - `source_url`
  - optional aliases / genre / adapter / style profile
- operator can now initiate a batch range without dropping to CLI memory:
  - glossary scan gate (`glossary-scan`)
  - bounded batch run with research readiness enforced
- this does not remove the explicit-approval rule for starting a new production batch

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

## Document Map

- `PROJECT_BRAIN.md`: project definition, architecture map, current verified state, guardrails, recovery memory.
- `IMPLEMENT_PLAN.md`: milestone plan, V3.10 protocol deliverables, future productization work, V4/V5 direction.
- `OPERATOR_MANUAL.md`: practical runbook, bounded batch start steps, and command guide.
- `00_Templates/Batch-Rollout-Checklist.md`: reusable operator checklist for bounded batches.
- `00_Templates/Worker-Bounded-Batch-Prompt.md`: reusable worker prompt template for bounded batches.
- `07_Reports/v3_10_repeatable_rollout_protocol.md`: repeatable rollout protocol and current V3.10 acceptance baseline.
- `07_Reports/glossary_conflicts_batch-ch019-ch023-v1.md`: current glossary conflict surface for V3.12.
- `07_Reports/glossary_audit_batch-ch019-ch023-v1.md`: per-chapter approved glossary usage audit for V3.12.
- `07_Reports/glossary_guard_batch-ch019-ch023-v1.md`: per-run evidence that current glossary guards reduce noisy deterministic scan candidates.
- `NOVEL_SETUP_PLAYBOOK.md`: step-by-step operator setup flow for a new novel project.
- `FETCH_ADAPTER_PLAYBOOK.md`: fetch adapter implementation and validation checklist.
- `RESEARCH_PROFILE_PLAYBOOK.md`: step-by-step research workflow using title plus source URL and external synopsis/review sources.
- `00_Templates/Novel-Profile.yaml`: canonical per-novel profile shape.
- `00_Templates/Research-Profile.yaml`: canonical research-profile scaffold.
- `D:\Fogust\Workspace\Novel\AGENTS.md`: global worker/agent behavior rules.
- `07_Reports/`: detailed historical reports and checkpoint evidence.
- `.system/config.yaml`: pipeline configuration entry point.
- `.system/style_profiles.yaml`: canonical style profile library and genre preset map.
- `.system/providers.yaml`: provider routing and retry/timeout configuration.

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

- `07_Reports/production_dry_run_batch_ch004_ch008_v2.md`
- `07_Reports/spot_check_batch_ch004_ch008_v2.md`

V3.8:

- `07_Reports/glossary_scan_batch-ch009-ch018-v1.md`
- `07_Reports/glossary_classification_batch-ch009-ch018-v1.md`
- `07_Reports/glossary_approval_decisions_batch-ch009-ch018-v1.md`
- `07_Reports/ch009_failed_block_recovery_gpt54.md`
- `07_Reports/ch009_block_006_qa_recovery.md`
- `07_Reports/v3_8_phase3_ch010_ch013_checkpoint.md`
- `07_Reports/v3_8_phase4_ch014_ch018_checkpoint.md`
- `07_Reports/spot_check_batch_ch014_ch018_v1.md`

V3.9:

- `07_Reports/glossary_scan_batch-ch019-ch023-v1.md`
- `07_Reports/glossary_classification_batch-ch019-ch023-v1.md`
- `07_Reports/glossary_approval_decisions_batch-ch019-ch023-v1.md`
- `07_Reports/spot_check_batch_ch019_ch023_v1.md`
