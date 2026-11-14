# Governance and detection repair

## Goal and check

Keep current controls bounded, derive chapter state instead of copying counts,
make evidence searchable, and measure reader-discovered escapes honestly.
Preserve all primary-checkout WIP and publication boundaries. No provider calls,
translation, content deployment, deletion, or self-approved merge is authorized.

## How / why

- Registry owns the intended public reader range; local output is not publication.
- Versioned generated Markdown is the clean-checkout reader input, not raw source.
- Raw, work, logs and final source-vault output are intentionally ignored/local.
- BRAIN and PLAN currently repeat historical checkpoints as current state.
- Sentinel writes two flat root reports per invocation, including retries.
- Its approved-term loader excludes non-Latin source terms: Chinese coverage is
  silently absent even though the downstream matcher already supports Chinese.
- Known-variant lists catch old incidents but do not establish semantic fidelity.
- Existing adoption tests pin policy bytes and append-only decisions; preserve
  these invariants while testing the new authoritative decision-log location.

Git history introduced append-only adoption decisions and integrity hashes for
recoverability. Those reasons still hold. Keeping all checkpoints in startup
documents and machine reports in a versioned flat directory does not follow from
them. Archive the old docs once, preserve decisions, and check current contracts.

## Selected interface

`python scripts/workspace_health.py {check,status,reports,quality}` is read-only.
`--root` selects an observed checkout; `--query` filters reports. JSON is the
output, so no generated dashboard/cache becomes another source of truth.

- `check`: document budgets, decision preservation, reader snapshot consistency,
  and quality-ledger validity; run in the existing CI job.
- `status`: desired registry range / versioned reader snapshot / observed local
  output / WIP, explicitly distinct; missing local data is unknown, not zero.
- `reports`: latest report per scope, paths to older evidence, no moves/deletes.
- `quality`: one incident per reader report, deduplicated publication exposure;
  partial retrospective data is a lower bound, not a claimed prospective rate.

Sentinel gains Chinese source-term coverage, explicit rejected-variant checks,
source-availability reporting, and non-overwriting generated report storage.
Historical regression mutations exercise the real staged gate, not a mock PASS.
This improves known semantic invariants; it is not general semantic verification.

## Procedure

- Audit/fix: isolated worktree; baseline tests and primary WIP hashes captured.
- Classify: GOVERNANCE, INCONSISTENT, FRAGILE, and missing detection coverage.
- Architect-lite: interfaces above; implement and verify them on real snapshots.
- Root tests and new mutation tests: passed locally; clean clone and isolated-venv
  install/tests also passed on local commit `f5dd38c01d0166f272f2050e11eda297398086c9`.
- Owner-approved landing/merged-SHA CI: pending; no approval inferred.

## Measured before / after

- Before: AGENTS 166, BRAIN 491, PLAN 551, ARCHITECTURE 150 lines. BRAIN/PLAN
  contained contradictory production checkpoints and obsolete provider statements.
- After: bounded current documents plus on-demand decisions/history. Startup needs
  only AGENTS and BRAIN plus observed status, not all historical plans/architecture.
- The status command observes registry/reader agreement while separately exposing
  extra local DSE/HGD/TDU files. It never promotes those extras into public scope.
- Root reports originally contain 1,521 flat files. They remain intact. The new
  index finds scope-specific evidence; new Lean and direct Sentinel runs use the
  ignored generated/month subtree, including retries. No cleanup-through-deletion
  or blanket ignore of existing reader WIP occurred.
- Three named historical reader incidents are backfilled with evidence. The
  retrospective snapshot ratio is explicitly a lower bound, not a publication-time
  rate. Verified future cohorts can be measured without pretending legacy history
  is complete; repeated generation does not increase the denominator.
- Existing low-worker quota/resource entitlement was not freshly verified.
  Medium/high design and implementation stayed with the main agent; no worker,
  paid provider, billing or account operation was started.

## Real product audit: detected backlog, NOT an all-clear

The new root Sentinel was run read-only against isolated copies of current local
source/output, with the current versioned glossaries: DSE ch140-ch160 and HGD
ch149/ch203/ch206. It evaluated original source for every inspected chapter.

- DSE: 18 blocker / 23 major / 10 minor glossary-coverage findings across 19
  chapters. These are unadjudicated source/output/glossary mismatches, **not 51
  confirmed semantic defects**. Examples include compound role/location terms.
- HGD: two existing paragraph-density blockers in ch149; the named historical
  voice/leakage strings are not present in this current local sample.
- Both runs exit failing as expected. These results are not waived. The current
  output files, public reader and source/checkpoints are not rewritten by this task.
  Inspector adjudication is required before republication of these affected ranges.
- Detailed machine findings and audit copies are local-only evidence. Hermetic
  mutation fixtures preserve the detector regressions without publishing raw text.

## Remaining ownership boundaries

The primary checkout changed concurrently after the captured baseline (including
source-readiness work and the other source-pending draft). This branch does not
stage, revert, or integrate those changes. An unchanged-primary-WIP claim cannot
be made across concurrent writers; all primary operations in this order were
read-only. Land/rebase this branch only after reviewing current ownership/diffs.

This repairs detection/governance, not every historical product issue. It does
not claim zero escaped defects, full semantic coverage, a clean primary tree,
live publication, merged status, or green CI for an unpushed commit.

## Verification and landing status

- Measured: governance implementation's clean clone installed the declared package
  in a fresh venv, passed 63 root tests, 11 Worker-envelope tests, the full legacy
  translation suite, and the governance command. No local source/output was present
  in that clone; Git stayed clean after tests. Source unavailability was reported
  as such rather than manufactured from machine state.
- Measured: doctor before on primary main had zero failures / one historical
  portability warning (401 files). Isolated-branch doctor after has zero failures,
  the expected no-upstream warning and the remaining historical portability warning
  (399 files). This is not a new merged-commit CI result.
- New novel work began only after that local clean-clone verification. It is a
  separate source-pending setup, with a disabled registry entry and no change to
  existing reader chapters. Final combined-branch verification is recorded below.
- Land steps 1-3/6/11: scope, CI/identity/policy, diff, real-surface diagnostics and
  doctor checked. Step 4: concurrent source-readiness work advanced default main to
  `ab13e65caf0edb334bebd68bc9dd230e4edd6ca8`; integrate it on this isolated branch,
  preserving both test sets, then recheck before any future merge.
- Steps 5/7/9/10: **pending/skip** because no push/publication or owner merge approval
  is inferred. No PR, remote exact-head CI, merge, branch deletion or deployment
  was performed. Step 8: no deployment/configuration switch to roll back; prior
  control/CI bytes and the base commit are retained.
- Principle decisions: **Lever over prose** produced one read-only command and CI
  checks; **Smallest change** kept existing evidence paths and used a compatibility
  shim instead of another scanner; **Claims carry evidence** kept historical ratios,
  source availability, unadjudicated findings and unmerged status explicit.

## Combined branch verification and second setup

Rebased this branch onto observed default `ab13e65caf0edb334bebd68bc9dd230e4edd6ca8`.
Resolved the CI command conflict by retaining **both** the concurrent source-fetch/
source-readiness tests and this branch's governance/mutation tests. No default
branch, prior WIP or external publication was changed by that rebase.

A clean clone at `9b16940ebf3f13c56965330cd11d807aabf67f3a` passed fresh-venv
installation, 83 root tests, governance checks, 11 Worker-envelope tests, the full
translation compatibility suite, `npm ci`, lint, production build and desktop/
mobile reader smoke. The input was the unchanged **versioned reader snapshot**,
not regenerated output from an absent corpus. Git stayed clean after all checks.
This is local measured evidence, not GitHub CI or a live deployment assertion.

The owner then added a second setup request: `Im a Young God Wont You Raise Me/`.
Both new vaults have their own voice/style, language guidance, English title/term
prompts, selected Code routes and disabled reader entries. Their research/source
state is pending with no imported bodies, approved pilot or production readiness.
The Young God listing explicitly says English translation; Rein_lout is recorded
as the listing account, with secondary original-author attribution kept separate.
No chapter-count/access/authorship claims are inferred from a platform badge.

Final local root tests now pass **86** cases. Additional regressions cover partial
missing source/product scopes and title-only source, preserve unknown historical
discovery dates rather than substituting repair dates, and keep green Sentinel
invariants separate from publication readiness (`safe_to_publish` remains unknown
on green, false on blocked). Report creation is exclusive so a filename collision
cannot overwrite earlier evidence. Both primary vault copies were verified with
line-ending-normalized text parity; existing primary registry/reader were untouched.

Before delivery, repeat the existing checks on the final commit/clone. Landing,
remote exact-head CI, and historical product-backlog adjudication remain separate
pending items. This report is closure evidence for the bounded implementation,
not a new checkpoint appended to startup controls.
