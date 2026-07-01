# V6.34 M6 HGD OOS Completion

Date: 2026-07-01

## Summary

Horror Game Developer out-of-sample run `v6-34-m6-hgd-oos-v1` completed all 10 locked OOS chapters in the isolated experiment vault.

This is experiment output only. No production `05_Output`, production glossary intent, production ledger intent, or MoonRead content was published from this run.

## Scope

Run ID: `v6-34-m6-hgd-oos-v1`

Experiment vault:

`Horror Game Developers/04_Work/_experiments/v6_34_m6_hgd_oos_v1`

Completed chapters:

- `ch015`
- `ch046`
- `ch060`
- `ch101`
- `ch131`
- `ch153`
- `ch184`
- `ch192`
- `ch226`
- `ch262`

## Final Status

Status command result:

- Records: `145`
- Completed blocks: `10/10`
- Current failed blocks: none
- Failed blocks: none
- Historical failed records: `4`
- Manual actions needed: none
- Next effective action: none

## Quality Checks

Latest scoped Sentinel results:

| Chapter | Sentinel counts | Safe |
|---|---|---|
| `ch015` | `0/0/0/0` | yes |
| `ch046` | `0/0/0/0` | yes |
| `ch060` | `0/0/0/0` | yes |
| `ch101` | `0/0/0/0` | yes |
| `ch131` | `0/0/0/0` | yes |
| `ch153` | `0/0/0/0` | yes |
| `ch184` | `0/0/0/0` | yes |
| `ch192` | `0/0/0/0` | yes |
| `ch226` | `0/0/0/0` | yes |
| `ch262` | `0/0/0/0` | yes |

Deterministic experiment-output checks:

- Han Chinese body text: none found
- Provider/meta leakage: none found
- Quote-only lines: `0`
- All final experiment outputs exist

## Provider And Failure Evidence

Provider/stage records:

| Provider | Stage | Status | Count |
|---|---|---|---:|
| `openrouter` | translating | completed | 11 |
| `openrouter` | refining | completed | 28 |
| `openrouter` | refining | failed | 1 |
| `openrouter` | formatting | completed | 11 |
| `openrouter_reasoning` | qa | completed | 11 |
| `qwen` | qa | completed | 1 |
| `local_recovery` | refining | completed | 5 |
| `local` | sentinel | completed | 31 |
| `local` | sentinel | failed | 1 |
| `local` | qa | hard_fail | 2 |

Important incidents during HGD OOS:

1. `ch131` stopped on glossary coverage failure for `Containment Department`.
   - Cause: HGD glossary conflict where `Containment Sector.md` aliased `Containment Department`.
   - Treatment: source-surface collision detection plus HGD alias cleanup.
2. `ch184` stopped on false glossary expectation for `Enter` inside `Entering` and semantic drift.
   - Treatment: boundary-aware glossary subset matching; reran block from translate after refine rerun false-passed semantic drift.
3. `ch192` stopped on peer-dialogue pronoun drift after literal-safe omission recovery.
   - Treatment: HGD-only peer-address repair after literal-safe recovery.

## Interpretation

HGD OOS ultimately reached a clean product-surface state for all 10 chapters, but it did not run smoothly unattended.

Evidence for improvement:

- All final scoped Sentinel reports are `0/0/0/0`.
- Known glossary/pronoun failure patterns were converted into targeted prevention mechanisms.
- No production artifacts were touched.

Evidence against long unattended scale:

- HGD OOS required multiple analysis/treatment loops.
- `local_recovery` was used five times.
- There were two QA hard-fails and one historical Sentinel failure.
- One QA fallback used `qwen`, which should be noted because current intended QA fallback avoids relying on qwen for normal production.

## Next Safe Action

Proceed to the next OOS slice, starting with DSE OOS, while keeping experiment output isolated.

After V6.34/M1-M7 completes, the user requested a future production task: continue DSE to end at `ch210`. Before starting that production work, verify the exact range because DSE is currently published through `ch180`; `ch181-ch210` is 30 chapters.

