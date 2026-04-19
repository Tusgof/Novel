# Project Brain: Deep Sea Embers Translation Pipeline

Last restored: 2026-04-19

This file is the project memory layer. It should preserve operational truth, current state, provider policy, recovery lessons, and next milestones. Do not shorten it into a tiny summary.

## Operating Model

- Codex is the architect, reviewer, orchestrator, and memory layer.
- Qwen/GPT workers are bounded implementers/operators. They must receive exact prompts with file scope, allowed changes, forbidden actions, validation, and final report format.
- Codex must verify disk state after every worker report. A worker report is not proof.
- Use Thai with the user. Use English for worker prompts, commands, code, and report templates when clearer.
- Do not run providers, resume, rerun-block, or modify ledger/artifacts unless the user explicitly approves that stage.

## Current Execution State

### Completed

- ch001-ch003: completed earlier baseline outputs exist.
- V3.7 complete: `batch-ch004-ch008-v2`
  - ch004-ch008 translated, QA-passed, formatted, assembled.
  - 28/28 blocks complete.
  - Outputs exist under `05_Output/ch004` through `05_Output/ch008`.
  - Spot-check verdict: acceptable for next larger batch.
- V3.8 complete: `batch-ch009-ch018-v1`
  - ch009-ch018 translated, QA-passed/recovered, formatted, assembled.
  - 53/53 blocks complete.
  - Outputs exist under `05_Output/ch009` through `05_Output/ch018`.
  - Current failed blocks: none.
  - Historical failed ledger records remain because `06_Logs/run_ledger.jsonl` is append-only.

### Current Batch

- V3.9 in progress: `batch-ch019-ch023-v1`
- Glossary scan-only gate: complete.
- Glossary approval gate: complete.
  - Approved:
    - `实太阳神` -> `สุริยเทพที่แท้จริง`
    - `面具神` -> `เทพหน้ากาก`
  - Rejected all other candidates from the scan.
  - Correct `glossary_approved` ledger records exist with block IDs `ch019`, `ch020`, `ch021`, `ch022`, `ch023`.
- Translation status:
  - `ch019-block-001`: complete.
  - `ch019-block-002`: complete after deterministic refined-text repair and post-format quote repair.
  - Next pending block: `ch019-block-003` at `translating`.
  - ch020-ch023: glossary-approved, translation not started.
  - ch024+: no processing should exist.
- Final outputs for ch019-ch023:
  - None expected yet. `05_Output/ch019/ch019.md` should not exist until all ch019 blocks complete.

## Important Reports

### V3.7

- `07_Reports/production_dry_run_batch_ch004_ch008_v2.md`
- `07_Reports/spot_check_batch_ch004_ch008_v2.md`

### V3.8

- `07_Reports/glossary_scan_batch-ch009-ch018-v1.md`
- `07_Reports/glossary_classification_batch-ch009-ch018-v1.md`
- `07_Reports/glossary_approval_decisions_batch-ch009-ch018-v1.md`
- `07_Reports/ch009_failed_block_recovery_gpt54.md`
- `07_Reports/ch009_block_006_qa_recovery.md`
- `07_Reports/v3_8_phase3_ch010_ch013_checkpoint.md`
- `07_Reports/v3_8_phase4_ch014_ch018_checkpoint.md`
- `07_Reports/spot_check_batch_ch014_ch018_v1.md`

### V3.9

- `07_Reports/glossary_scan_batch-ch019-ch023-v1.md`
- `07_Reports/glossary_classification_batch-ch019-ch023-v1.md`
- `07_Reports/glossary_approval_decisions_batch-ch019-ch023-v1.md`

## Provider Routing Policy

- Gemini:
  - term extraction
  - literal translation
  - QA fallback only on provider failure
- Claude:
  - term suggestions
  - primary refinement
- GPT-5.4 via Codex:
  - first refinement fallback after Claude failure
  - must pass deterministic validation and Qwen QA before commit
- Qwen:
  - second refinement fallback
  - QA judge
- Local Python:
  - formatting
  - ledger/status/bookkeeping

Hard rules:

- Do not use Claude for literal translation or QA.
- If Gemini literal translation hits quota/capacity, wait/resume. Do not silently fallback to Claude for translation.
- Provider quota/error/meta text must never be committed as successful output.
- Windows argv command-length preflight exists for Gemini.
- If QA hard-fail escalates to a manual prompt in a noninteractive worker, stop and report. Do not force-accept automatically.

## Worker Model Policy

- Allowed for state-changing implementation:
  - Codex/GPT workers with exact bounded prompts.
  - Qwen DeepSeek Chat/Reasoner when available and explicitly scoped.
- Disallowed for state-changing work:
  - Elephant
  - Nemotron

Reason: during V3.9 glossary approval, Elephant and Nemotron both reported successful ledger appends while disk verification showed missing or incorrect state. They are not reliable for ledger/artifact/code/config operations.

If used at all, Elephant/Nemotron may only do read-only drafting/checklists/reports, and Codex must verify real files afterward.

## Glossary Policy

- Human-in-the-loop approval is mandatory for new glossary terms.
- Use longest-match, non-overlapping term retrieval.
- Reject substrings/fragments/noisy candidates unless explicitly approved.
- Approved notes live in `01_Glossary/`.
- Quarantined/deprecated false positives remain in `01_Glossary/quarantine/`.
- Never create glossary notes for rejected candidates.
- `glossary_approved` ledger records must use chapter IDs exactly, e.g. `ch019`, not `ch019-glossary-approved`.

## Recovery Lessons

- The ledger is append-only. Historical failed records may exist even when current status is clean.
- Always inspect latest stage state per block rather than counting failed records naively.
- `command_too_long` in Gemini QA fallback can often be recovered with bounded QA-stage rerun if Qwen primary succeeds later.
- Claude can crash on Windows with return code `3221225786`; retry may succeed. If not, GPT-5.4 fallback is valid for refinement.
- QA hard-fails are usually real semantic issues. Inspect `*.qa.json`, compare literal/refined/source, repair only the necessary artifact, then rerun from the failed stage.
- Formatting can introduce punctuation drift after QA. For repaired blocks, inspect `*.formatted.json` for lost dialogue quotes.
- Do not trust worker summaries without checking:
  - artifact existence
  - JSON content
  - ledger latest records
  - no `ch024+` records when the range is ch019-ch023
  - no forbidden file changes

## V4 Product Direction

The project is not just one novel script. It should become a practical operator tool for translating multiple novels and genres.

Required product capabilities:

- Multi-novel support:
  - per-novel config/profile
  - separate source/output/work/glossary namespaces
  - source adapter selection per site/source
- Multi-genre support:
  - per-genre style profiles
  - per-novel translation brief
  - glossary and tone guidance can differ by genre
- Novel research profile:
  - gather synopsis/style/review context from reliable external sources when setting up a novel
  - store concise profile so the user does not need to paste large context
- Operator UI/window:
  - run scan-only gate
  - view glossary candidates
  - approve/reject/select one of several Thai term options
  - resume bounded translation
  - inspect current blockers
  - generate reports
- Better automation:
  - bounded resume until chapter/range
  - chapter checkpoint command
  - automatic report generation
  - provider usage/cost report
  - richer glossary conflict detector

## Next Immediate Step

Continue V3.9 from `batch-ch019-ch023-v1`:

1. Verify `ch019-block-002` remains complete and clean.
2. Resume bounded checkpoint from `ch019-block-003`.
3. Stop immediately on QA hard-fail/manual prompt.
4. Do not process ch024+.
5. After ch019 completes, run output cleanliness checks before continuing wider.
