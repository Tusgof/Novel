# Control-document recovery

Paths are repository-relative. Git is the normal history/recovery mechanism;
inspect the diff and preserve WIP before any owner-authorized restore.

## Current SHA256 (LF bytes)

| file | sha256 |
| --- | --- |
| `AGENTS.md` | `6dff6a274f3e380ea5cbb982d8ce267e0c2f8b9d8b34efc934f32d918b366991` |
| `PROJECT_BRAIN.md` | `32c2330f2daa5d99fc8ab0022b94f1c411bcc6675fff1f377300c1621ac7ba5c` |
| `IMPLEMENT_PLAN.md` | `0e663dd4fba4bfb326e52e95dc6319dbb8409f51a0588e778b9ad4a475f34045` |
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
