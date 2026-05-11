# Implement Plan

Last restored: 2026-04-19

This plan defines what remains before the project is genuinely usable. Keep it practical and operational.

## Current State Snapshot

- ch001-ch018 outputs exist.
- V3.7 complete: `batch-ch004-ch008-v2`
  - 28/28 blocks complete.
  - Production dry-run passed deterministic checks and spot-check.
- V3.8 complete: `batch-ch009-ch018-v1`
  - 53/53 blocks complete.
  - ch009-ch018 outputs exist.
  - current failed blocks: none.
  - historical failed ledger records exist and are expected.
- V3.9 in progress: `batch-ch019-ch023-v1`
  - fetched: ch019-ch023 complete.
  - glossary_scanned: ch019-ch023 complete.
  - glossary_approved: ch019-ch023 complete.
  - approved glossary terms:
    - `实太阳神` -> `สุริยเทพที่แท้จริง`
    - `面具神` -> `เทพหน้ากาก`
  - translated/completed so far:
    - `ch019-block-001`
    - `ch019-block-002`
  - next pending stage: `ch019-block-003` at translating.
  - ch020-ch023 not translated yet.
  - no ch024+ processing allowed.

## Milestone V3.9: ch019-ch023 Controlled Batch

Goal: complete ch019-ch023 with the same safety level as V3.8, but with tighter bounded checkpoints because noninteractive workers can hit manual QA prompts.

### Stage 1: Preflight

- Read:
  - `PROJECT_BRAIN.md`
  - `AGENTS.md`
  - `OPERATOR_MANUAL.md`
  - `06_Logs/run_ledger.jsonl`
- Verify:
  - glossary approvals exist for `ch019` through `ch023`
  - no translation/refinement/QA/formatting records for ch020-ch023 before starting
  - no ch024+ records for this run
  - glossary notes exist:
    - `01_Glossary/实太阳神.md`
    - `01_Glossary/面具神.md`

### Stage 2: Bounded ch019 Completion

- Continue from `ch019-block-003`.
- Preferred worker mode:
  - process one block or a small bounded chapter segment
  - stop on QA hard-fail/manual prompt
  - stop on provider command_too_long if normal rerun does not clear it
- Do not force-accept QA failures without user/Codex review.
- After ch019 all blocks complete:
  - verify `05_Output/ch019/ch019.md` exists
  - run cleanliness checks:
    - no provider/meta text
    - no Chinese body text except title if expected
    - no wrong glossary variants
    - no quote-only lines
    - no obvious formatting drift around dialogue quotes

### Stage 3: ch020-ch023 Translation

- Proceed in bounded checkpoints.
- Recommended split:
  - ch020-ch021
  - ch022-ch023
- Stop conditions:
  - QA hard-fail
  - provider auth/quota/capacity failure
  - repeated command_too_long
  - unexpected ch024+ activity
  - final output cleanliness failure

### Stage 4: V3.9 Final Gate

- Verify:
  - all expected blocks complete
  - outputs exist for ch019-ch023
  - current failed blocks none
  - no ch024+ processing
  - glossary notes unchanged except approved terms
  - no provider/meta leakage
- Create:
  - V3.9 checkpoint report
  - spot-check report for ch019-ch023
- Update:
  - `PROJECT_BRAIN.md`
  - `Implement_PLAN.md`
  - `OPERATOR_MANUAL.md`
  - `AGENTS.md`

## Milestone V3.10: Larger Stable Rollout

Goal: prove the pipeline can repeat reliably over larger ranges without manual chaos.

Candidate range: decide after V3.9, likely 5-10 chapters depending on provider stability.

Requirements:

- scan-only glossary gate
- human glossary approval
- bounded translation checkpoints
- automatic final-output checks
- spot-check report
- documentation sync
- no unverified worker claims

## Milestone V4.0: Practical Operator Product

Goal: make the system usable by the user without relying on Codex memory for every step.

### V4.0A: Local Operator Window

Must support:

- select project/novel
- run scan-only gate
- view glossary candidate table
- approve/reject terms
- select one Thai term from 2-3 suggestions
- run/resume bounded translation
- show current run status and blocker
- open relevant artifact/report paths

Priority is usability and correctness, not visual polish.

### V4.0B: Multi-Novel Support

Required:

- per-novel project profile
- per-novel folder layout
- per-novel glossary namespace
- per-novel source adapter config
- per-novel style brief
- output paths isolated by novel

The user specifically wants this to support many novels and genres, not just Deep Sea Embers.

### V4.0C: Multi-Genre Style Profiles

Required:

- genre style presets
  - dark nautical fantasy
  - xianxia/wuxia
  - modern urban
  - sci-fi
  - horror
  - romance/drama
- translation instructions per genre
- glossary category preferences per genre
- QA criteria per genre

### V4.0D: Novel Research Profile

When setting up a new novel, do not infer genre/style from one chapter only.

Preferred workflow:

- search web for novel title, synopsis, reviews, tags, and style discussion
- summarize:
  - premise
  - genre
  - tone
  - narration style
  - recurring terminology
  - reader expectations
- save concise profile in project config/report
- use this profile in translation/refinement prompts

### V4.0E: Automation Improvements

- `resume --until chXXX` or equivalent bounded command.
- `status --chapter chXXX`.
- automatic checkpoint report generator.
- provider usage/cost report.
- glossary conflict detector:
  - substring conflicts
  - quarantine conflicts
  - existing approved term overlap
  - noisy candidate detection
- post-format dialogue punctuation check.

## V4 Done Criteria

The project is product-ready when:

- A new novel can be configured without code edits.
- A genre/profile can be selected or generated.
- The user can run scan-only, glossary approval, translation, recovery, and report generation from a local operator interface.
- Glossary decisions can be made in a UI/window.
- Each stage has deterministic validation.
- Failed blocks can be recovered without ad hoc instructions.
- Reports and documentation update with minimal manual writing.
- Provider routing and fallbacks are visible to the operator.
- Worker models with false-completion risk are blocked from state-changing tasks.

## Worker Model Restrictions

- Elephant: do not use for state-changing tasks.
- Nemotron: do not use for state-changing tasks.
- Allowed only for read-only draft/report/checklist tasks with Codex disk verification.
- Reason: both gave false completion reports during V3.9 glossary approval attempts.

## Immediate Next Step

Resume V3.9 carefully:

1. Create a bounded worker prompt for `ch019-block-003` onward.
2. Do not allow force-accept.
3. Stop on manual QA prompt.
4. Verify artifacts and ledger after each checkpoint.
5. Continue to ch020-ch023 only after ch019 output gate passes.
