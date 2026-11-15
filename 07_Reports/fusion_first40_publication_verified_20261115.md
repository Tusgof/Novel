# Fusionpunk Code ch001-ch040 — verified public release

**Measured:** owner-approved PR [#16](https://github.com/Tusgof/Novel/pull/16)
merged by rebase at `474a6be1a7614c3c84dbb1d399a86e40b7f100d4`. The owner explicitly
approved merging this PR when its exact-head CI passed. No approval was inferred
for Gacha ch041+ or Investing publication.

- PR-head `tests` run 43712134863 passed on
  `8a29ecdf214e799dabc833ad568f7024073da6b2`; Vercel preview checks also passed.
- Default-branch `tests` run
  [43713325990](https://github.com/Tusgof/Novel/actions/runs/43713325990) completed
  successfully on the exact merged SHA, not merely the latest listed run.
- GitHub deployment 7803354470 records **Production**, the same merged SHA and
  successful deployment status. Public book page shows exactly forty Code rows:
  https://novel-pink-nu.vercel.app/books/a-gacha-addicts-fusionpunk-life
- Live ch001/ch013/ch024/ch028/ch032/ch040 each returned HTTP 200. Titles and
  `[Code]` labels match; **every rendered paragraph** in each of these six
  chapters matches the accepted generated Markdown. Unreleased Gacha ch041 and
  Investing chapter URLs return the intended 404. There is no public-range drift.

The scoped local reader acceptance and its preservation/semantic limits remain
in `fusion_first40_reader_inspector_20261115.md`. Existing six-book chapter and
manifest bytes were retained; aggregate library/import reports intentionally add
the seventh book. Raw/run/source-bearing evidence remains local, not a public
translation corpus. No source fetch, routing change or production write beyond
the authorized first-forty reader was performed during landing.

Vercel MCP inspection could not access the owning team with this connection.
No new OAuth grant, credential extraction or profile bypass was attempted. The
deployment claim instead uses the exact-SHA GitHub deployment/status and actual
unauthenticated public-page evidence above; Vercel internal runtime logs are not
claimed inspected. Browser-specific local results remain Windows/Chromium; live
paragraph comparison is HTTP evidence, not an all-browser semantic certificate.

The publication cohort records this first verified forty once. Repeated builds
and unchanged regeneration must not add exposure. Translation work for the
already-authorized extensions continues in the original Worker worktree/base;
the separate landing branch preserved incoming main source metadata through
ch082 without expanding the accepted translation or public release range.
