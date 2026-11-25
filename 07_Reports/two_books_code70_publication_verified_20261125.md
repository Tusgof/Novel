# MoonRead Code chapters 61–70: two-book live publication

**Measured:** both authorized ranges are live on [MoonRead](https://novel-pink-nu.vercel.app), which now
serves 70 `[Code]` chapters for each book. No chapter 071 was translated or published.

- [PR #24](https://github.com/Tusgof/Novel/pull/24) was rebase-merged at
  `edc4d08ef02206fb1e974d66d34b764868ce8843`. The deployed reader tree matches the checked PR head
  `c9fda2abfff2ac46525f8e20ee63527e99bedfac`. The exact PR head passed
  [CI](https://github.com/Tusgof/Novel/actions/runs/45593972658) and Vercel Preview.
- [Exact main CI](https://github.com/Tusgof/Novel/actions/runs/45594619485) passed. GitHub Production deployment
  `8054746595` reported `success` on that merged SHA. The previous rollback
  point was deployment `7828080267`, revision `7349baef`, with both books at 60.
- On the public hostname, `2026-11-25T10:26:58.054Z` verification checked all 20 new chapter
  URLs and 2,939 rendered paragraphs against accepted Markdown, with
  matching titles, `[Code]` labels, chapter navigation, and both 70-entry TOCs.
  Both chapter 071 routes returned 404. Chromium 148.0.7778.96 passed 20 desktop/
  mobile chapter samples with no horizontal overflow or browser errors. The two
  cover assets matched the unchanged release-tree bytes.

## Scope, regression protection, and limits

Independently accepted Thai output was imported without prose changes (only the
reader's existing newline/trailing-space normalization). The 1,102 unchanged
generated files include both old 1–60 chapter sets and unrelated book snapshots.
The scoped gate measured 8 books, 834 available, 0 missing/rejected and Sentinel
0/0/0/0 with 20 sources. Lint, 855-page build, smoke, generator 7/7, reader 6/6,
root 91/91, envelope 11/11 and Deep Sea Embers tests passed detached from WIP.

The additional mobile review reproduced Investing ch063 at 530px wide on a
390px viewport because its 36-character status rule was unbreakable. The
paragraph-only `overflow-wrap: anywhere` fix preserves authored text and
newlines. The browser test was red on the old build and green on the fix. CI
was pinned to Ubuntu 24.04 after the hosted `ubuntu-latest` image outpaced the
current Playwright browser support. No gate was skipped or loosened.

Only these 20 first-publication episodes were added to the incident ledger.
No new incident is claimed: the layout defect was caught before publication.
Provenance and translation checkpoints stay local; public verification checks
the stated invariants and rendered text, not universal semantic fidelity.
