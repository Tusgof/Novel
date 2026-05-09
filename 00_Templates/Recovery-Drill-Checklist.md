# Recovery Drill Checklist

Use this checklist when you need to prove that the project can recover canonical memory safely without pulling runtime artifacts into git.

## Scope

This checklist is for:

- `PROJECT_BRAIN.md`
- `Implement_PLAN.md`
- `OPERATOR_MANUAL.md`

It is not for:

- `03_Raw/`
- `04_Work/`
- `05_Output/`
- `06_Logs/`

Those runtime directories stay outside git recovery and must not be restored from source control.

## Preconditions

Run from project root:

```powershell
cd "D:\Fogust\Workspace\Novel\Deep Sea Embers"
$env:PYTHONIOENCODING='utf-8'
```

Confirm current repo state:

```powershell
git status -sb
novel-pipeline --config ".system/config.yaml" preflight
novel-pipeline --config ".system/config.yaml" report recovery-drill
```

Expected:

- repo is inside a git work tree
- `origin` exists
- canonical docs are tracked and restorable from `HEAD`
- runtime dirs are ignored and untracked

## Recovery Procedure

### A. Inspect before touching anything

Capture current state:

```powershell
git status --short
git rev-parse --short HEAD
novel-pipeline --config ".system/config.yaml" report preflight
novel-pipeline --config ".system/config.yaml" report recovery-drill
```

If the incident includes translation/runtime state concerns, also capture:

```powershell
novel-pipeline --config ".system/config.yaml" status --run-id <run_id>
```

### B. Restore canonical docs only

Restore one file:

```powershell
git restore --source=HEAD --worktree -- PROJECT_BRAIN.md
```

Restore all canonical docs:

```powershell
git restore --source=HEAD --worktree -- PROJECT_BRAIN.md Implement_PLAN.md OPERATOR_MANUAL.md
```

Do not restore runtime directories from git.

### C. Verify restored content

Check file set and clean tree:

```powershell
git status --short
```

If the docs are supposed to match the committed baseline exactly, the tree should be clean.

If you intentionally re-applied current verified state after restore, verify content with:

```powershell
python -m compileall novel_pipeline
python test_translation.py
novel-pipeline --config ".system/config.yaml" preflight
novel-pipeline --config ".system/config.yaml" report product-review --run-id batch-ch019-ch023-v1
```

### D. Reconstruct current state only from evidence

If a doc must be rebuilt beyond `HEAD`, use only:

- `07_Reports/`
- `06_Logs/run_ledger.jsonl`
- deterministic CLI status / preflight / report outputs

Do not reconstruct from memory alone.

### E. Re-commit if needed

If the restored/rebuilt docs are now the correct source of truth:

```powershell
git add PROJECT_BRAIN.md Implement_PLAN.md OPERATOR_MANUAL.md
git commit -m "Restore canonical project docs"
git push origin main
```

## Stop Conditions

Stop and escalate if:

- `report recovery-drill` is not accepted
- runtime dirs show up as tracked
- canonical docs are missing from `HEAD`
- git remote/origin is unavailable
- you are tempted to restore `03_Raw/`, `04_Work/`, `05_Output/`, or `06_Logs/` from git

## Evidence To Keep

At minimum, keep:

- `07_Reports/preflight_report.md`
- `07_Reports/recovery_drill.md`
- any relevant `product_review_*.md`
- the commit hash used for restore
