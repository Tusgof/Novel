# Preflight Report

## Summary
- status: degraded
- workspace_root: D:\Fogust\Workspace\Novel\Deep Sea Embers
- config_path: D:\Fogust\Workspace\Novel\Deep Sea Embers\.system\config.yaml
- next_safe_action: Continue only with bounded operations while warnings remain.

## Providers
| provider | status | resolved_path | prompt_transport | stages | working_dir |
| --- | --- | --- | --- | --- | --- |
| claude | ready | C:\Users\ASUS\AppData\Roaming\npm\claude.cmd | stdin | term_suggestion:fallback | none |
| codex | ready | C:\Users\ASUS\AppData\Roaming\npm\codex.cmd | stdin | fetch, literal_translation:fallback, project_setup, qa_judge:fallback, refinement:fallback, term_extraction:fallback | none |
| openrouter | ready | C:\Users\ASUS\AppData\Local\Programs\Python\Python314\python.EXE | stdin | formatting, formatting:fallback, literal_translation, literal_translation:fallback, qa_judge:fallback, refinement, refinement:fallback, refinement:fallback, term_extraction, term_extraction:fallback, term_suggestion, term_suggestion:fallback | none |
| openrouter_reasoning | ready | C:\Users\ASUS\AppData\Local\Programs\Python\Python314\python.EXE | stdin | qa_judge | none |
| qwen | ready | C:\Users\ASUS\AppData\Roaming\npm\qwen.cmd | stdin | qa_judge:fallback, refinement:fallback | none |

## Research Readiness
- status: active
- readiness: ready
- bounded_translation_ready: yes
- translation_ready: yes
- missing_fields: none
- warnings: none
- blocking_reasons: none
- next_safe_action: Research profile is ready for normal production.

## Git Guardrails
- available: yes
- in_work_tree: yes
- branch: main
- head: 38cc6b8
- origin: https://github.com/Tusgof/Novel.git
- working_tree: dirty
- git_warnings: Working tree is dirty.
- ignored_generated_changes: none

## Workspace
- missing_directories: none
- warnings: Working tree is dirty; commit or stash before large write actions.
- blocking_reasons: none
