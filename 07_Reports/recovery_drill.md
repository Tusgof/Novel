# Recovery Drill Report

## Summary
- overall_status: accepted
- workspace_root: D:\Fogust\Workspace\Novel\Deep Sea Embers
- branch: main
- head: ee1c058
- origin: https://github.com/Tusgof/Novel.git
- next_safe_action: Recovery baseline is ready. Use git restore for canonical docs and keep runtime state out of git.

## Acceptance Checks
| check | status | detail |
| --- | --- | --- |
| git_work_tree | ok | inside git work tree |
| remote_origin | ok | https://github.com/Tusgof/Novel.git |
| canonical_docs_restorable | ok | all canonical docs tracked and restorable from HEAD |
| runtime_dirs_ignored | ok | runtime directories are ignored and untracked |

## Canonical Docs
| path | tracked | restorable_from_head | detail |
| --- | --- | --- | --- |
| PROJECT_BRAIN.md | yes | yes | tracked and restorable |
| Implement_PLAN.md | yes | yes | tracked and restorable |
| OPERATOR_MANUAL.md | yes | yes | tracked and restorable |

## Runtime Ignore Policy
| path | ignored | tracked_entries | detail |
| --- | --- | ---: | --- |
| 03_Raw | yes | 0 | ignored and untracked |
| 04_Work | yes | 0 | ignored and untracked |
| 05_Output | yes | 0 | ignored and untracked |
| 06_Logs | yes | 0 | ignored and untracked |
