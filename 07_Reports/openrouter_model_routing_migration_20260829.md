# OpenRouter Model Routing Migration

Date: 2026-08-29

## Decision

- Replace `google/gemini-3-flash-preview` with `google/gemini-3.7-flash`.
- Replace `deepseek/deepseek-v4-flash` with `deepseek/deepseek-v4-flash-0731`.
- Remove `deepseek/deepseek-v4-pro` from production QA fallbacks.
- Keep historical reports and benchmark scripts unchanged because they describe models actually tested at that time.

## Scope

Updated production routing for Deep Sea Embers, Horror Game Developers, Infinite Regressor Stories, and Immortality System. Updated available `providers.default.yaml` snapshots so future resets do not restore retired model IDs.

## Verification

- OpenRouter model metadata lists both new IDs and their text/reasoning parameters.
- Gemini 3.7 Flash short probe returned `OK` with a sufficient output budget.
- DeepSeek V4 Flash 0731 returned `OK` in normal and reasoning-enabled modes.
- Structured routing regression checks cover all four production configs and reject DeepSeek V4 Pro in QA fallbacks.
- `python -m compileall novel_pipeline`: passed.
- `python test_translation.py`: passed.
- All four production preflights parsed the new routing; degraded state before commit was only the expected dirty-worktree warning.

## Immortality System Checkpoint

The in-flight old-model formatter completed before cancellation and produced a content-preserving `ch011` artifact. The interrupted Sentinel run was repeated explicitly:

- output guardrail: passed
- scoped Sentinel: blocker/major/minor/info `0/0/0/0`
- report: `07_Reports/sentinel_quality_immortality-system-ch011-routing-migration_20260829_032011.md`

The migration applies to subsequent provider calls. Next safe action is the bounded `ch012-block-004` repair from refinement.

## First Production Call

- DeepSeek V4 Flash 0731 completed `ch012-block-004` refinement.
- The reasoning QA request was then closed by the remote host after 42.53 seconds (`WinError 10054`), so strict provider-stop halted without fallback.
- Artifact inspection found the new refined phrase `ไม่สามารถขั้นสร้างฐาน`. This exposed a gap in the first bare-`築基` rejected-variant rule, which covered `จะ`, `ยังไม่`, and `การ` but not the modal `ไม่สามารถ`.
- The novel glossary, registry guardrail, and regression coverage were expanded for `ไม่สามารถขั้นสร้างฐาน` before any further provider call.

This evidence is insufficient to claim that the new models are better than the retired routes. Health and refinement passed, while production QA reliability remains unproven.
