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
| `PROJECT_BRAIN.md` | `A7FF741F24A0168D6D8BA2BC55247C0876FDEC50A8C946A1C6DE7C63320C2526` |
| `IMPLEMENT_PLAN.md` | `0B2EC85E9CB11162EA21C558D71A4D3EB00F66FC692B19B9D70B0DFC932C74A7` |
| `ARCHITECTURE.md` | `A11B85D26597361C41190CF1F5963AA8897880CEF5F01D044E790AA20D60E2C8` |

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
