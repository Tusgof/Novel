# Canonical Doc Recovery

Last updated: 2026-06-23

This workspace keeps the three canonical control files at `D:\Fogust\Workspace\Novel`, outside the nested `Deep Sea Embers` git repository.

Canonical files:

- `D:\Fogust\Workspace\Novel\AGENTS.md`
- `D:\Fogust\Workspace\Novel\PROJECT_BRAIN.md`
- `D:\Fogust\Workspace\Novel\IMPLEMENT_PLAN.md`

Current SHA256 hashes after the latest root-doc sync:

| file | sha256 |
| --- | --- |
| `AGENTS.md` | `6401F23239C17F28153C7319435474F21B604217A857B44442FDD74E80368BC1` |
| `PROJECT_BRAIN.md` | `AEC3A7577D6069008364C64DCBE61E5996A5025B7CF6BB3772393B4DA9D76D22` |
| `IMPLEMENT_PLAN.md` | `819682C34C93D997AFE2BC11AE00FE9442F5764049A3F0EAA9D0C9CE57F4225B` |

Latest local snapshot:

- `D:\Fogust\Workspace\Novel\99_Adhoc_Scripts\canonical_docs_backup_20260616_v618_runtime_slice`

## Check Integrity

```powershell
cd "D:\Fogust\Workspace\Novel"
Get-FileHash AGENTS.md,PROJECT_BRAIN.md,IMPLEMENT_PLAN.md -Algorithm SHA256
```

## Backup

Use a dated folder outside any novel-specific directory:

```powershell
cd "D:\Fogust\Workspace\Novel"
$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$target = "D:\Fogust\Workspace\Novel\99_Adhoc_Scripts\canonical_docs_backup_$stamp"
New-Item -ItemType Directory -Force -Path $target
Copy-Item AGENTS.md,PROJECT_BRAIN.md,IMPLEMENT_PLAN.md,DOC_RECOVERY.md -Destination $target
Get-FileHash "$target\AGENTS.md","$target\PROJECT_BRAIN.md","$target\IMPLEMENT_PLAN.md" -Algorithm SHA256
```

## Restore

Only restore these files if they are damaged or accidentally overwritten:

```powershell
cd "D:\Fogust\Workspace\Novel"
$backup = "D:\Fogust\Workspace\Novel\99_Adhoc_Scripts\canonical_docs_backup_20260616_v618_runtime_slice"
Copy-Item "$backup\AGENTS.md" .
Copy-Item "$backup\PROJECT_BRAIN.md" .
Copy-Item "$backup\IMPLEMENT_PLAN.md" .
Get-FileHash AGENTS.md,PROJECT_BRAIN.md,IMPLEMENT_PLAN.md -Algorithm SHA256
```

## Rules

- Do not store durable cross-novel planning inside a single novel folder.
- Do not let worker models rewrite these files without Codex review.
- If a worker report conflicts with these files, inspect disk state before updating the docs.
- If these hashes change intentionally, update this file in the same turn.
