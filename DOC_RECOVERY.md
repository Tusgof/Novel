# Canonical Doc Recovery

Last updated: 2026-06-16

This workspace keeps the three canonical control files at `D:\Fogust\Workspace\Novel`, outside the nested `Deep Sea Embers` git repository.

Canonical files:

- `D:\Fogust\Workspace\Novel\AGENTS.md`
- `D:\Fogust\Workspace\Novel\PROJECT_BRAIN.md`
- `D:\Fogust\Workspace\Novel\IMPLEMENT_PLAN.md`

Current SHA256 hashes after the latest root-doc sync:

| file | sha256 |
| --- | --- |
| `AGENTS.md` | `4C5F58BA5682F19441541DE86DFCE9A96F061D4BF13A9E0C90424CB8FA51552B` |
| `PROJECT_BRAIN.md` | `AE55371F6B4D3326C8A307A888240D5EE87F34476A7A4277DCD83FC7E064DD2E` |
| `IMPLEMENT_PLAN.md` | `239A87472EF0EBA26CD5B59D51FE8D5C1123B602B6D7645A7B78D3A9AC5D29A1` |

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
