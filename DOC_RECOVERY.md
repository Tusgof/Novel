# Canonical Doc Recovery

Last updated: 2026-10-08

This workspace keeps the canonical control files at `D:\Fogust\Workspace\Novel`, outside any single-novel folder.

Canonical files:

- `D:\Fogust\Workspace\Novel\AGENTS.md`
- `D:\Fogust\Workspace\Novel\PROJECT_BRAIN.md`
- `D:\Fogust\Workspace\Novel\IMPLEMENT_PLAN.md`
- `D:\Fogust\Workspace\Novel\ARCHITECTURE.md`

Current SHA256 hashes after the latest root-doc sync:

| file | sha256 |
| --- | --- |
| `AGENTS.md` | `43CE3D0264DFF0205AD65B913B55A9246F30AAFD2539FE1B6C75D4C748D9CFCE` |
| `PROJECT_BRAIN.md` | `1B00DCD60615E8CD8934498387F906B91D4E4B3A1D6E3E874D6B607A2EAE2E0D` |
| `IMPLEMENT_PLAN.md` | `0CEA8854C698697C73AEF6997317A848AF7ADCEEAEF25B6F01C1374722034A8C` |
| `ARCHITECTURE.md` | `6BA998315978C7691913683CC3A500DE4B7E8DE116323FFFAC7361A656A1F9D2` |

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
