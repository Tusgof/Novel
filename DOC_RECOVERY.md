# Canonical Doc Recovery

Last updated: 2026-10-03

This workspace keeps the canonical control files at `D:\Fogust\Workspace\Novel`, outside any single-novel folder.

Canonical files:

- `D:\Fogust\Workspace\Novel\AGENTS.md`
- `D:\Fogust\Workspace\Novel\PROJECT_BRAIN.md`
- `D:\Fogust\Workspace\Novel\IMPLEMENT_PLAN.md`
- `D:\Fogust\Workspace\Novel\ARCHITECTURE.md`

Current SHA256 hashes after the latest root-doc sync:

| file | sha256 |
| --- | --- |
| `AGENTS.md` | `F555A6FFCF5583FFB990E857365DBCA66EDEBCEFBDF79D0493B9CF25CBFC4B41` |
| `PROJECT_BRAIN.md` | `B42DDF4D8CE63D2A28DFB1E18377113C9DC10D678FF5E188A0A345B25990D6BE` |
| `IMPLEMENT_PLAN.md` | `847EE963E607AC3BDCAE4B1BDA74AE8E1C6120489305CD0B6AC944B40D41F60F` |
| `ARCHITECTURE.md` | `12AE192AEB9899CF5EE96FD02A0B9C591266CC4ABE51DDBC4B00E5CE259988B1` |

Latest local snapshot:

- `D:\Fogust\Workspace\Novel\99_Adhoc_Scripts\canonical_docs_backup_20260616_v618_runtime_slice`

## Check Integrity

```powershell
cd "D:\Fogust\Workspace\Novel"
Get-FileHash AGENTS.md,PROJECT_BRAIN.md,IMPLEMENT_PLAN.md,ARCHITECTURE.md -Algorithm SHA256
```

## Backup

Use a dated folder outside any novel-specific directory:

```powershell
cd "D:\Fogust\Workspace\Novel"
$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$target = "D:\Fogust\Workspace\Novel\99_Adhoc_Scripts\canonical_docs_backup_$stamp"
New-Item -ItemType Directory -Force -Path $target
Copy-Item AGENTS.md,PROJECT_BRAIN.md,IMPLEMENT_PLAN.md,ARCHITECTURE.md,DOC_RECOVERY.md -Destination $target
Get-FileHash "$target\AGENTS.md","$target\PROJECT_BRAIN.md","$target\IMPLEMENT_PLAN.md","$target\ARCHITECTURE.md" -Algorithm SHA256
```

## Restore

Only restore these files if they are damaged or accidentally overwritten:

```powershell
cd "D:\Fogust\Workspace\Novel"
$backup = "D:\Fogust\Workspace\Novel\99_Adhoc_Scripts\canonical_docs_backup_20260616_v618_runtime_slice"
Copy-Item "$backup\AGENTS.md" .
Copy-Item "$backup\PROJECT_BRAIN.md" .
Copy-Item "$backup\IMPLEMENT_PLAN.md" .
Copy-Item "$backup\ARCHITECTURE.md" .
Get-FileHash AGENTS.md,PROJECT_BRAIN.md,IMPLEMENT_PLAN.md,ARCHITECTURE.md -Algorithm SHA256
```

## Rules

- Do not store durable cross-novel planning inside a single novel folder.
- Do not let worker models rewrite these files without Codex review.
- If a worker report conflicts with these files, inspect disk state before updating the docs.
- If these hashes change intentionally, update this file in the same turn.
