# Repository Guidelines

## Agent Operating Model

Codex is the architect, orchestrator, reviewer, and project memory layer. Worker models are implementers/operators for bounded tasks only. Codex must inspect context, decide the intended solution, define edge cases, write exact worker prompts, and verify real files/artifacts/ledger after each worker report.

Use Thai with the user by default. Use English for worker prompts, commands, code, and report templates when clearer.

Do not trust worker self-reports without disk verification. The project has already had false completion reports from free OpenRouter models.

## Project Structure

Project root:

```text
D:\Fogust\Workspace\Novel\Deep Sea Embers
```

Important paths:

- `novel_pipeline/`: Python package and CLI implementation.
- `novel_pipeline/pipeline.py`: main orchestrator.
- `novel_pipeline/stages/`: fetch, glossary, translate, refine, QA, format.
- `.system/`: config, provider routing, provider retry policy, style profiles.
- `01_Glossary/`: approved/deprecated glossary notes.
- `03_Raw/`: fetched source.
- `04_Work/`: block artifacts.
- `05_Output/`: final Markdown outputs.
- `06_Logs/run_ledger.jsonl`: append-only ledger.
- `07_Reports/`: scan/classification/approval/checkpoint/spot-check reports.
- `PROJECT_BRAIN.md` and `Implement_PLAN.md`: read before substantive work.

## Commands

Use UTF-8:

```powershell
$env:PYTHONIOENCODING='utf-8'
```

Deterministic checks:

```powershell
python -m compileall novel_pipeline
python test_translation.py
```

Status:

```powershell
novel-pipeline --config ".system/config.yaml" status --run-id batch-ch019-ch023-v1
```

Resume only with explicit approval:

```powershell
novel-pipeline --config ".system/config.yaml" resume --run-id batch-ch019-ch023-v1
```

Targeted rerun only with exact block and stage:

```powershell
novel-pipeline --config ".system/config.yaml" rerun-block --run-id batch-ch019-ch023-v1 --block-id ch019-block-002 --from-stage qa
```

## Model And Provider Policy

Current routing:

- Gemini: term extraction and literal translation.
- Claude: term suggestions and primary refinement.
- GPT-5.4 via Codex: first refinement fallback.
- Qwen: second refinement fallback and QA judge.
- Gemini: QA fallback only on provider failure.
- Local Python: formatting.

Rules:

- Do not use Claude for literal translation or QA.
- If Gemini literal translation hits quota/capacity, wait and resume. Do not silently fallback to Claude.
- GPT-5.4 fallback outputs require deterministic validation and Qwen QA before commit.
- Provider quota/error/meta output must never be committed.
- Windows argv command-length preflight protects Gemini from command-line-too-long failures.
- QA hard-fail manual prompts must stop in noninteractive execution; do not auto force-accept.

## Worker Model Restrictions

Do not use Elephant or Nemotron for state-changing work.

Forbidden for Elephant/Nemotron:

- ledger appends
- glossary approvals
- code/config edits
- artifact edits
- pipeline recovery
- resume/rerun operations
- translation checkpoints
- force-accept decisions

Reason: during V3.9 glossary approval, Elephant and Nemotron falsely reported successful ledger appends while real disk verification showed the state was missing/incorrect.

They may only be used for read-only draft/report/checklist tasks where false completion cannot change state, and Codex must verify the output.

## Worker Prompt Requirements

Every worker prompt must specify:

- Qwen execution level:
  - `Chat-level implement`
  - `Reasoning-level implement`
- exact files to read
- exact files allowed to change
- behavior to implement
- constraints and edge cases
- validation commands/checks
- forbidden actions
- required final report format

Do not ask workers to "figure out the solution" broadly. Codex owns architecture.

## Current State

- V3.7 complete: `batch-ch004-ch008-v2`.
- V3.8 complete: `batch-ch009-ch018-v1`.
- ch001-ch018 outputs exist.
- V3.9 in progress: `batch-ch019-ch023-v1`.
  - glossary scan and approval complete.
  - approved terms: `实太阳神`, `面具神`.
  - `ch019-block-001` complete.
  - `ch019-block-002` complete after refined-text repair and formatted quote repair.
  - next pending: `ch019-block-003` translating.
  - ch020-ch023 translation not started.
  - no ch024+ processing allowed.

## Recovery Pattern

- Check latest block state, not just raw failed counts, because ledger is append-only.
- For QA hard-fail:
  - inspect `*.qa.json`
  - compare source/literal/refined/formatted
  - repair the narrowest artifact
  - rerun from the failed stage only
  - do not force-accept without user/Codex approval
- For Claude crash:
  - retry may succeed
  - if not, GPT-5.4 fallback is valid for refinement
- For Gemini `command_too_long`:
  - use bounded QA rerun when appropriate
  - do not switch translation to Claude
- After any formatting repair:
  - check no Han Chinese
  - check no provider/meta text
  - check no quote-only lines
  - check dialogue quote punctuation did not drift

## Documentation Rule

Do not compress `PROJECT_BRAIN.md`, `Implement_PLAN.md`, `OPERATOR_MANUAL.md`, or this file into tiny summaries. These files are operational memory and must preserve commands, paths, current state, policies, and recovery lessons.
