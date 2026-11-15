# Control-document recovery

Paths are repository-relative. Git is the normal history/recovery mechanism;
inspect the diff and preserve WIP before any owner-authorized restore.

## Current SHA256 (LF bytes)

| file | sha256 |
| --- | --- |
| `AGENTS.md` | `4d63935b798a14101668b4b136fe26efd4a24687251f36c574264368f75d3416` |
| `PROJECT_BRAIN.md` | `886bdd6189041352c40b73e90d496e9033239ef05f028c0bf2b05ea002b7220e` |
| `IMPLEMENT_PLAN.md` | `040a31e2f433e19e6acedb6e9c5a3e4f753863697943e7cab1c4da8976c4131d` |
| `ARCHITECTURE.md` | `bdaada76598a2d19291fa368b03a83556f51a97867f7b67308d920e8e94ce4d8` |

The CI integrity test verifies these hashes. An intentional edit updates its hash
in the same change; a hash is integrity evidence, not proof of current truth.

## Compaction / rotation

- `python scripts/workspace_health.py check` enforces both line and character
  budgets. Keep current state in BRAIN, open outcomes in PLAN and boundaries in
  ARCHITECTURE. Close/rewrite items instead of appending checkpoints indefinitely.
- Put durable incident/prevention evidence in the quality ledger/report, then
  link it. Generated Sentinel evidence belongs in the ignored generated subtree.
- Read `DECISIONS.md` only for a relevant policy decision; preserve its prior rows
  and append superseding decisions when authorized. It is not a startup document.
- The one-time pre-compaction snapshot and byte hashes are in
  `Backup_/governance/2026-11-15/manifest.json`. Earlier policy archives retain
  their original bytes. Use an archive only after diagnosing the damage; do not
  overwrite valid current documents with a historical checkpoint.
