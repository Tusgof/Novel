# MoonRead Code chapters 71–75: verified publication

**Measured:** the authorized release added 10 `[Code]` chapters to
[MoonRead](https://novel-pink-nu.vercel.app), five per book. Each of these two TOCs now has 75 entries.
No episode 76 is published by this release.

- [PR #29](https://github.com/Tusgof/Novel/pull/29) passed exact-head tests
  and was rebase-merged at `7b2f74cf6cfd2829c677d44270d15af00ea97744`. [Exact main CI](https://github.com/Tusgof/Novel/actions/runs/45676001886) passed.
- GitHub Production deployment `8066170686` reported `success`. Previous
  rollback point: deployment `8065499226`, revision `579ef744db5346b609f05fa5bcea92beea108e94`.
- The public verification at `2026-11-25T18:35:33.135Z` matched all 10 new routes and
  1,418 rendered paragraphs to the independently accepted text.
  It checked headings, `[Code]` labels, adjacent chapter links, both complete
  TOCs, both 070→071 transitions, and 404 for both chapter 076 routes.
- Chromium 148.0.7778.96 passed 20 mobile/desktop chapter samples; no
  horizontal overflow or browser errors. Both live cover assets match the
  unchanged release-tree bytes.
- Scoped generation, Sentinel, lint, build, smoke and reader regressions
  passed. The release diff contains only registry range updates, ten chapter
  snapshots and generated metadata. All older chapters, unrelated snapshots,
  covers and reader code were unchanged. A green gate is not a proof of all
  semantic fidelity.

Only these 10 first-publication IDs are recorded here. No new reader incident
is asserted. The ledger append does not change the reader.
