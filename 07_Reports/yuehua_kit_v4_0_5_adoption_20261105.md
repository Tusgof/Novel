# Yuehua Kit v4.0.5 adoption — 2026-11-05

## Outcome and scope

Governance-only adoption for the Novel repository and its six registered novels.
Keep **UNIT / T2**, active state, and the existing real surface: final translated
chapters, output guardrails/Sentinel, and the MoonRead reader. No product route,
source, glossary, checkpoint, ledger, output, reader content, other agent, main
model, account, billing, privacy, OAuth, MCP, browser installation, or other
repository is changed by this adoption.

Prerequisite Go routing was separately owner-approved and landed in
[PR #12](https://github.com/Tusgof/Novel/pull/12), merged SHA
`0595265ce1d059a6384a35074f6ac95f37f3ef50`. The required `tests` workflow passed
on that exact SHA: [run 41979363954](https://github.com/Tusgof/Novel/actions/runs/41979363954).
The primary checkout fast-forward preserved SHA256 baselines for all 121
pre-existing modified/untracked files. This adoption starts from that merged SHA.

## Verified release, not main

**Measured:** the remote latest release is stable, non-draft/non-prerelease
[v4.0.5](https://github.com/Tusgof/Yuehua-Kit/releases/tag/v4.0.5).
Its annotated tag object is `9fbeff0c23626cc967673287f1b096be1f081828`;
the peeled commit and detached temporary checkout HEAD both equal
`5af741b76e5c51442917d41af5ff91ec8ddc90bd`. README, CHANGELOG, AGENTS,
browser/execution policies, the update prompt, start-unit, land, and the decision
log were read from this verified tag checkout. No unapproved main/working branch
was substituted.

Relevant decisions: K-007 requires byte-identical policy archives; K-024
supersedes only the BrowserOS-default portions of K-001/K-021 while retaining
security; K-025 adds low-only execution and immediate main-model fallback.
K-005/K-010 owner/CI/reviewer authority and K-022 repository/level boundaries
remain. K-023 allows the owner-approved idea; it is not inference-performance or
quota evidence. No separate Novel decision requiring BrowserOS was found.

## Installed skills and fallback

**Measured:** installed `yuehua-mode/INSTALLED_FROM.json` reports v4.0.3 at
`e3db9a3754f4d6b37b86bc90290ebe318d0915da`. Running the verified release's
`install-skills --dry-run` proposed updating yuehua-mode/land for Claude and
Codex. No actual installation or `--force` was run; foreign skills/local edits
remain untouched. This task follows the verified temporary checkout's v4.0.5
skills and CLI instead. No shared-skill update means no restart for that purpose;
OpenCode reloads the project-local agent profile automatically.

Reasoning demand for the contract/authority adoption is medium/high and remains
with the lead. Scoped native usage inspection returned no usable Go allowance
or overage-safety evidence. No low-worker inference was dispatched: the existing
main model continued immediately, with no worker partial work to reconcile.
No credential, privacy, region, Extra Usage, payment, or fallback-provider change
was made. The fresh read-only policy-verification child inherited the main model;
it was not routed through the new low worker.

## Start-unit checklist and boundaries

1. **Level and tier.** Retained confirmed UNIT/T2 and the recorded owner rationale. No downgrade or new level.
2. **Version it.** Existing hosted repository and green default-branch CI retained; work isolated in `yuehua-kit-v4.0.5`.
3. **Pin the kit.** Lock records the verified version/commit/adoption date; other valid lock fields remain identical.
4. **Name the real surface.** Existing translated-output/Sentinel/MoonRead surface retained; policy is also checked in a fresh agent session.
5. **Minimum verification for the tier.** Retain all T2 checks; add only cheap adoption/archive/control checks to existing CI.
6. **Control documents, short.** Surgical contract merge, append-only Decision #8, and updated control hashes. Previous AGENTS and the decision-log-bearing BRAIN archived before replacement. Read the existing control gates first.
7. **Verification skill and Feature Map.** Add the kit-adoption feature and practical commands.
8. **Check.** Released doctor, unit regressions, clean-clone checks and actual native registration; landing remains subject to owner approval and exact-head/merged-SHA CI.

**By level:** this is one UNIT with children inside this repository. The six
novels keep their registry, routes and quality gates. ORG audit/portfolio work is
skipped because this is not an ORG. Moving-a-v3-unit steps are not a new migration
here (already v4.0.3), but their surgical merge, preserved stronger rules,
append-only adoption and read-the-gate requirements are followed. Nothing in
another repository or shared installation is migrated.

## Changes and byte provenance

- `.yuehua-kit.json`, `AGENTS.md`: released pin, K-024 vendor neutrality, K-025 low-only delegation, no weakened gates, and explicit exposure handling.
- `policies/agent-browser.md` and `policies/execution-workers.md`: exact released Git-blob bytes. Authority, credential/resource/cap, vault, profile isolation, remote exposure, OAuth, prompt-skipping and evidence rules are preserved.
- `.opencode/agents/execution-worker.md`: no same-named profile existed before adoption. Start from the released profile, preserving default-deny/file-work behavior, then add deny rules for the unit's extra canonical control files. Existing `novel-worker` and default/main model are unchanged.
- `Backup_/policy/2026-11-05_pre-v4.0.5/`: pre-change AGENTS SHA256 `43ce3d0264dff0205ad65b913b55a9246f30aafd2539fe1b6c75d4c748d9cfce`; BRAIN SHA256 `3c523581213487eb0bd9d7c05cc8165fb93d9a1534ce235eb7913b1bc8edd586`. Existing decision rows are unchanged, in order.
- `.gitattributes`: archives are byte-preserved, and copied policies/profile are LF-pinned for reproducible checks.
- `PROJECT_BRAIN.md`, `IMPLEMENT_PLAN.md`, `DOC_RECOVERY.md`: adoption decision/current work, prior routing landing evidence, and refreshed control hashes; history is preserved.
- `.agents/skills/novel-verify/references/features/README.md` and `kit-adoption.md`: current operating/verification pointers, including how to avoid stale shared-skill policy.
- `test_kit_adoption.py`, `.github/workflows/tests.yml`: pin/state, archives, append-only decisions, policy bytes, stronger unit rules, permission outcomes, unchanged other agents/routes, and control hashes checked in the existing T2 job.

## Measured verification

- Root tests: **39 passed**, including seven new adoption checks; Worker-envelope tests: **11 passed**; full DSE regression script passed. Compile and diff checks pass.
- Native OpenCode lookup was explicitly scoped to this worktree and the returned location checked. `execution-worker` resolved as a subagent to `opencode-go/deepseek-v4.1-flash#low`. Effective rules allow normal in-workspace file read/edit and deny shell, execute/MCP, web/network tools, recursive subagents, external directories and canonical control-file edits. This is metadata/permission verification, not an inference or quota test.
- The existing `novel-worker` still resolves to DeepSeek `high`; the main/default remains `codex-lb/gpt-6.1-sol`. Six product provider files and the existing profile match the baseline checksums.
- A fresh child session reported v4.0.5, vendor-neutral browser choice and immediate main-model fallback from its automatically supplied project instructions **before file reads**. Its seven allowed reads found no blocking contradiction; edits=0. This verifies actual fresh-session contract use, not just a lock-file number.
- Doctor before adoption on main: no failure, one existing portability warning (401 historical doc/data/test/example files). Branch doctor after adoption has no failures and an expected unpushed-branch warning in addition to historical portability findings. Final tracked/archive count and clean-clone evidence are recorded before landing.

**Unverified / not run:** Go allowance, overage safety, low-worker inference,
live quota-exhaustion/failure handover, and cross-platform live inference are not
claimed as passed. Product source/translation/reader checks are not rerun as a
publication because no product content changes. Existing provider-free Sentinel
and promotion regressions remain in the required suite.

## Landing status

This adoption is prepared locally; its push/PR, exact-head CI, owner merge
approval and merged-SHA CI are not claimed complete here. The earlier explicit
push/merge approval applied to routing PR #12. Request bounded authority for the
Kit change before new external writes. No self-approval. Rollback reference is
`0595265ce1d059a6384a35074f6ac95f37f3ef50`; use a reviewed follow-up rather than
resetting the protected primary checkout.

**Inferred:** the pinned local pointers plus the measured fresh-session read
should prevent inheriting the older installed browser policy. This is not a
claim that shared user-level skills were upgraded or that all future harnesses
will automatically select the correct release.
