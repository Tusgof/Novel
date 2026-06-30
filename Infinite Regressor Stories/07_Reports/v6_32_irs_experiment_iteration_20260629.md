# V6.32 IRS Experiment Iteration Report

Status: IN-SAMPLE FAILED GATE

Created: 2026-06-29

## Scope

- Novel: Infinite Regressor Stories
- Experiment vault: `Infinite Regressor Stories/04_Work/_experiments/v6_32_vault`
- Baseline report: `04_Work/_experiments/v6_32_vault/07_Reports/v6_32_irs_experiment_baseline_20260628_191451.md`
- In-sample run: `irs-v6-32-insample-treatment-v2`
- In-sample chapters: `ch009`, `ch018`, `ch019`, `ch003`, `ch004`, `ch005`, `ch006`, `ch007`, `ch008`, `ch020`
- Out-of-sample chapters held back: `ch021`, `ch023`, `ch026`, `ch032`, `ch034`, `ch035`, `ch038`, `ch040`, `ch044`, `ch055`

Out-of-sample was not run because the in-sample gate failed.

## Fixes Implemented Before/During The Iteration

Layer 0 / multi-novel:

- Added deterministic Zalgo/source-noise normalization before block splitting.
- Added regression coverage for runaway combining-mark sound effects.
- Added `rejected_variants` support to glossary entries.
- Added deterministic rejected-variant repair after refinement and QA retry refinement.
- Added QA blocking for rejected glossary variants.

Layer 1 / English-to-Thai:

- Added embedded CJK-with-English-gloss normalization for non-CJK source texts.
- Updated IRS literal/refinement prompts to translate or Thai-transliterate embedded CJK instead of preserving CJK characters.

Layer 2 / IRS:

- Reduced IRS `non_chinese_word_limit` from `1500` to `900` to lower omission/truncation risk.
- Added `ทะเลเหลือง` as a rejected variant for `West Sea -> ทะเลตะวันตก`.

## Measured Result

In-sample treatment v2:

- Ledger records: 91
- Completed blocks: 8/34
- Completed chapters: 2/10 (`ch009`, `ch018`)
- Current failed block: `ch019-block-002`
- Final outputs created in experiment vault: `ch009.md`, `ch018.md`
- Out-of-sample: not started

Provider/stage highlights:

- `openrouter` translating completed: 9
- `openrouter` refining completed: 23
- `openrouter` refining failed: 1 timeout
- `openrouter_reasoning` QA completed: 3
- `openrouter_reasoning` QA failed: 1, after fallback chain reached Codex quota
- `qwen` QA completed: 5
- `local_recovery` refining completed: 3

## Failure

Failed block: `ch019-block-002`

Latest QA failure:

```text
Provider 'codex' returned unusable output (quota).
```

Context:

- The block originally failed QA because refined output omitted two monster roar beats from source/literal.
- Literal-safe recovery regenerated a complete refined draft.
- QA fallback chain then failed when Codex fallback hit quota.
- Earlier in the same run, Qwen fallback hung and had to be killed manually before the parent pipeline continued.

## Decision

V6.32 is not production-ready.

Do not run IRS long batches or chapter-level parallel batches yet. The in-sample gate failed before out-of-sample could start.

## Next Safe Action

Run a V6.32 follow-up iteration before any IRS production scaling:

1. Remove Codex from normal IRS QA fallback, or make it opt-in only for manual recovery.
2. Add hard subprocess cleanup for Qwen fallback so a child process cannot hang the parent pipeline indefinitely.
3. Prefer OpenRouter `deepseek/deepseek-v4-flash` reasoning as primary QA, with a bounded non-Codex fallback policy.
4. Rerun `ch019-block-002` from QA in the experiment vault after the fallback policy fix.
5. If recovered, rerun the full in-sample gate as `irs-v6-32-insample-treatment-v3`.
6. Start out-of-sample only after in-sample reaches zero current failed blocks, zero blocker/major quality findings, and no manual process kills.

Production recommendation: blocked until V6.32 in-sample passes.
