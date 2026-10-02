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

## Removed verified obsolete files

The following 18 files were removed after reference checks:

- six obsolete MoonRead development log files
- five obsolete Playwright text snapshots/logs
- four ignored HGD one-off repair Python scripts
- three tracked HGD one-off repair CJS scripts

The tracked script deletions are visible in git history. No raw source,
translation output, ledger, glossary, experiment trace, report, backup, or
deployment file was removed.

## Transient candidates

`__pycache__`, MoonRead `.next`, the remaining MoonRead `.playwright-cli`, and
local git backup objects remain generated/archive state. Recursive deletion of
these binary or cache trees was rejected by the host command policy. `.gitignore`
now excludes the MoonRead Playwright capture directory and root-level MoonRead
logs; `.next` was already ignored. These directories remain physically present
and are documented rather than force-deleted.

## Safety decision

No raw source, translation output, ledger, glossary, experiment trace, report,
backup, or deployment file was deleted or moved. This preserves recovery and
auditability while removing verified obsolete scripts and future worktree noise
from generated MoonRead captures/logs.
