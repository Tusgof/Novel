# Two-book interim Code publication verified

**Measured:** owner-approved PR [#18](https://github.com/Tusgof/Novel/pull/18)
merged by rebase at `01795d12c1e32d2841011254ce5d71af878a402e`.
The owner explicitly approved merging on green CI and an evidence-only follow-up
after actual live verification. The release is Fusionpunk ch001-ch045 and
Investing in My Crippled Wife ch001-ch016, not unaccepted later products.

- PR-head tests run [43745424444](https://github.com/Tusgof/Novel/actions/runs/43745424444)
  passed on `22fd0bdfc3ffabba580997e942c98628d1a0cbd6`; preview checks passed.
- Default-branch tests run [43747317393](https://github.com/Tusgof/Novel/actions/runs/43747317393)
  passed on the exact merged SHA above, including Linux reader build/regressions.
- No automatic production deployment for that SHA was observed. After the owner
  completed the Vercel team-access consent, the same connection successfully read
  the intended team/project and confirmed production still served `13802d6`.
  One production deployment was then created from the exact accepted merged SHA,
  inheriting existing project/build settings without route, domain or config edits.
- Vercel deployment `dpl_7vVsQhNEEj1HFnmbWBmt6eCnKsq6` is **READY**, target
  **production**, commit `01795d12c1e32d2841011254ce5d71af878a402e`, with
  `novel-pink-nu.vercel.app` assigned and no alias error. Build events confirm
  cloning that commit and deployment completion. GitHub deployment **7808372969**
  independently records successful Production status on the same SHA.

## Actual public surface

Unauthenticated live HTTP checks completed at **2026-11-15T19:06:15Z**:

- https://novel-pink-nu.vercel.app/books/a-gacha-addicts-fusionpunk-life
  shows exactly45 consecutive available chapters, all labeled `[Code]`.
- https://novel-pink-nu.vercel.app/books/investing-in-my-crippled-wife
  shows exactly16 consecutive available chapters, all labeled `[Code]`.
- All **61 chapter pages returned200**. Every title and translator label matches;
  all **12,112 rendered paragraphs** match the accepted generated Markdown, not
  merely a short preview, first paragraph or chapter-count string.
- Fusionpunk46 and Investing17/21/56 direct reader URLs return404. No promoted,
  quarantined or noncontiguous setup-only chapter silently entered this release.

Local source/chain/Sentinel, desktop/mobile reader, preservation and semantic
limits are detailed in `two_books_interim_reader_inspector_20261116.md`.
The live comparison is HTTP rendering evidence, not a fresh all-browser visual
test or a general semantic-fidelity certificate. The six unrelated reader books
and the forty previously public Fusionpunk chapter blobs remain unchanged.

## Exposure accounting and remaining scope

Append exactly two verified cohorts: Fusionpunk **ch041-ch045** and Investing
**ch001-ch016**. These are21 new distinct first-published chapters; retain the
original first-forty cohort without counting it again. Rebuilding, deployment
retries and this evidence-only update are not new publication exposure.

Source/run artifacts remain local ignored evidence. Translation continues under
separate bounded Inspector/Worker acceptance; the owner requested another reader
update once each authorized sixty-chapter scope is completely accepted. Neither
a Worker RETURN nor local promotion proves that final scope is already complete.

The user-approved Vercel connection retains the team grant. No secrets were read,
new login bypass attempted, settings changed or paid alternate/top-up enabled.
The missing automatic deployment's underlying cause is **unverified**; manual
deployment completion does not prove a Git integration repair.
