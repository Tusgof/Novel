# Recursive Workspace Organization Audit

## Scope

All files and subdirectories under `D:\Fogust\Workspace\Novel`, including
novel vaults, MoonRead, experiment vaults, backups, reports, and local runtime
state.

## Inventory snapshot

Top-level active areas are the canonical control docs, shared config/assets,
research logs, reports, scripts, five novel vaults, MoonRead, and archival
backups. Novel raw/work/output/log trees and historical experiments are ignored
by git but are retained as product/evidence data.

## Retained by policy

- Root control docs and shared pipeline source
- Each novel's `.system`, `.obsidian`, glossary, raw source, work artifacts,
  final output, logs, reports, and recovery backups
- MoonRead source, deployment config, dependencies, and generated reader data
- Historical experiments and Sentinel reports needed to explain prior decisions
- `99_Adhoc_Scripts` backups; these are archival and not runtime dependencies

## Transient candidates

`__pycache__`, MoonRead `.next`, MoonRead `.playwright-cli`, and MoonRead dev
logs were identified as generated local state. Recursive deletion was attempted
with explicit workspace-relative paths but was rejected by the host command
policy, so no destructive deletion was claimed. `.gitignore` now excludes the
MoonRead Playwright capture directory and root-level MoonRead logs; `.next` was
already ignored. These directories remain physically present until a permitted
cleanup operation is available.

## Safety decision

No raw source, translation output, ledger, glossary, experiment trace, report,
backup, or deployment file was deleted or moved. This preserves recovery and
auditability while removing future worktree noise from generated MoonRead
captures/logs.
