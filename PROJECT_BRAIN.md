# Project Brain

Current intent and unresolved risks only. Replace stale state; do not append
checkpoint histories here. CI enforces line and character budgets.

## What is authoritative now

- Publication intent: `00_Config/novel_registry.json`. A local output file is
  neither independent acceptance nor permission to publish it.
- Reader snapshot: versioned `MoonRead/content/generated/`. This is what a clean
  checkout can build. It is not proof of what the live deployment currently serves.
- Local source/run/output: the selected novel's ignored runtime folders. They
  may contain additional or incomplete work; their absence in a clone is unknown,
  not evidence that translation never happened.
- Current routing: the selected `.system/providers.yaml`; historical provider
  names and billing records are not the current route or remaining quota.
- Approved terms and voice: each novel's glossary, profile and voice policy.
- Work scope: the current owner order; roadmap entries never grant execution,
  spending, publication, routing or merge authority.

## Read current state, do not copy chapter totals

```powershell
python scripts/workspace_health.py status
python scripts/workspace_health.py quality
```

The commands distinguish registry targets, reader snapshot, observed local files,
and uncommitted WIP. They do not probe a deployment, start a worker or modify files.
For the run's actual promotion/quarantine state, use the Feature Map's status path.

## Active risks / limits

- Semantic fidelity is not proven by a green gate. Source-backed term checks
  catch specific invariants; QA and Inspector reading still miss meaning errors.
- The focused historical audit exposes unadjudicated glossary/layout backlog;
  affected old ranges are not newly certified: see the governance repair report.
- Reader incident history is retrospective and incomplete. The quality command
  labels its historical ratio a lower bound, not evidence of an improving process.
- Extra local chapters require a new bounded acceptance/publication decision.
- The primary checkout has preserved WIP. Inspect Git before writes; never hide
  it with reset, stash, blanket ignore rules or an unapproved content push.
- Shared installed Kit skills may be older than `.yuehua-kit.json`; use the
  pinned procedures. Unverified included allowance means main-agent fallback.
- Existing private TDU delivery and the source-pending Fusionpunk draft are local
  work, not new public registry entries. The local reader process may be stopped.

## Where to go next

- Active outcomes: `IMPLEMENT_PLAN.md`; boundaries: `ARCHITECTURE.md` on demand.
- Verification commands/gotchas: `.agents/skills/novel-verify/references/features/README.md`.
- Evidence search: `python scripts/workspace_health.py reports --query <scope>`.
- Append-only decisions: `DECISIONS.md` (including original Decision Log #3).
- Pre-compaction history: `Backup_/governance/2026-11-15/`; recovery: `DOC_RECOVERY.md`.
