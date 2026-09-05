# OpenRouter Model Routing Migration

Date: 2026-08-29

## Decision

- Replace `google/gemini-3-flash-preview` with `google/gemini-3.7-flash`.
- Replace `deepseek/deepseek-v4-flash` with `deepseek/deepseek-v4-flash-0731`.
- Remove `deepseek/deepseek-v4-pro` from production QA fallbacks.
- Keep historical reports and benchmark scripts unchanged because they describe models actually tested at that time.

## Scope

Updated production routing for Deep Sea Embers, Horror Game Developers, Infinite Regressor Stories. Updated available `providers.default.yaml` snapshots so future resets do not restore retired model IDs.

## Verification

- OpenRouter model metadata lists both new IDs and their text/reasoning parameters.
- Gemini 3.7 Flash short probe returned `OK` with a sufficient output budget.
- DeepSeek V4 Flash 0731 returned `OK` in normal and reasoning-enabled modes.
- Structured routing regression checks cover all four production configs and reject DeepSeek V4 Pro in QA fallbacks.
- `python -m compileall novel_pipeline`: passed.
- `python test_translation.py`: passed.
- All three production preflights parsed the new routing; degraded state before commit was only the expected dirty-worktree warning.
