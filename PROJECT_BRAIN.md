# Project Brain: Deep Sea Embers Translation Pipeline

Last updated: 2026-04-20
Last verified: 2026-04-20 after runtime safety controls were implemented and pushed in commit `f2143f6`; verified with `python -m compileall novel_pipeline`, `python test_translation.py`, `status --run-id batch-ch019-ch023-v1`, and `inspect-block --block-id ch019-block-002`

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
| Multi-novel config/profile | 0 | 2 | 2 | later |
| Operator UI/window | 0 | 2 | 2 | later |
| Cosmetic UI polish | 1 | 0 | 1 | deferred |

Implemented runtime safety controls:

- `resume --manual-action-mode stop` prevents noninteractive EOF by exiting with manual-action status instead of prompting.
- `resume --until-chapter <chapter_id>` and `resume --until-block <block_id>` allow bounded production checkpoints.
- `inspect-block --run-id <run_id> --block-id <block_id>` is a read-only block inspection tool.
- `status` now prints current failed blocks, historical failed records, and next effective action.
- formatting now rejects provider/meta leakage, Han Chinese text, and quote-only lines before committing successful formatted artifacts.

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

- V3.9 in progress: `batch-ch019-ch023-v1`
- glossary scan-only gate: complete
- glossary approval gate: complete
- approved terms:
  - `实太阳神` -> `สุริยเทพที่แท้จริง`
  - `面具神` -> `เทพหน้ากาก`
- correct `glossary_approved` ledger records exist with block IDs `ch019`, `ch020`, `ch021`, `ch022`, `ch023`
- `ch019-block-001`: complete
- `ch019-block-002`: complete after deterministic refined-text repair and post-format quote repair
- next pending block: `ch019-block-003` at `translating`
- ch020-ch023: glossary-approved, translation not started
- ch024+: must remain unprocessed
- final outputs for ch019-ch023: none expected yet

## Next Safe Action

Continue V3.9 in a bounded checkpoint:

1. Inspect `ch019-block-002` if needed:
   `novel-pipeline --config ".system/config.yaml" inspect-block --run-id batch-ch019-ch023-v1 --block-id ch019-block-002`
2. Resume only through ch019, with noninteractive manual-action stop:
   `novel-pipeline --config ".system/config.yaml" resume --run-id batch-ch019-ch023-v1 --until-chapter ch019 --manual-action-mode stop`
3. Stop immediately if the command exits with manual action required, provider failure, command-length error, formatting validation failure, or any ch024+ activity.
4. Do not force-accept QA failures.
5. After ch019 completes, verify `05_Output/ch019/ch019.md` before continuing to ch020-ch023.

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
- Formatting drift: formatting can remove dialogue quote marks after QA passes.
- Mojibake/encoding errors: reports or artifacts can display corrupted Chinese/Thai if encoding is mishandled.
- Worker false completion: unreliable free models may claim state changes that did not occur.
- Documentation overwrite: memory docs were previously shortened/damaged by worker edits before git backup existed.

## Recovery Playbooks

### QA hard-fail

1. Stop the run.
2. Read source, literal, refined, formatted if present, and `*.qa.json`.
3. Identify the exact omission or meaning drift.
4. Repair the narrowest artifact only if deterministic repair is justified.
5. Rerun from the failed stage, usually `qa`.
6. Verify QA, formatting, ledger, and cleanliness.

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

## Document Map

- `PROJECT_BRAIN.md`: project definition, architecture map, current verified state, guardrails, recovery memory.
- `Implement_PLAN.md`: milestone plan, future productization work, V4/V5 direction.
- `OPERATOR_MANUAL.md`: practical runbook and command guide.
- `AGENTS.md`: worker/agent behavior rules.
- `07_Reports/`: detailed historical reports and checkpoint evidence.
- `.system/config.yaml`: pipeline configuration entry point.
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
