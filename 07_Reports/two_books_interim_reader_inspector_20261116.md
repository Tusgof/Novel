# Two-book interim Code reader release

**Measured, local release candidate:** Fusionpunk ch001-ch045 and Investing in My
Crippled Wife ch001-ch016. The owner explicitly requested completed chapters on
MoonRead now and a second update after both authorized translations finish.
This supersedes the previous Fusionpunk first-forty-only publication limit for
this accepted interim cohort; translation and final-release gates remain intact.

## Accepted scope and isolation

- Fusionpunk ch041-ch045 passed independent source reading and its original
  five-chapter dependency checker, including the resolved ch041 quarantine.
- Investing's corrected mandatory setup20 and PROD-A were independently accepted.
  Five original frozen groups were rechecked, covering every consecutive episode
  ch001-ch016. The noncontiguous setup samples are deliberately not published.
- Active/newly promoted translation products are excluded. Investing PROD-B has
  an unresolved ch019 QA conflict; none of that batch enters this snapshot.
- The landing tree starts from merged `13802d6`; the original translation branch,
  frozen inputs, primary WIP and incoming source-access metadata remain untouched.
  The existing Fusionpunk source ceiling at ch082 is preserved, not broadened.

## Verification

- Scoped generation: **8 books, 755 available, 0 missing, 0 rejected**; exactly
  45 Fusionpunk and 16 Investing consecutive rows carry `[Code]`.
- All 61 generated chapters equal accepted Markdown after only the generator's
  newline/trailing-whitespace normalization. All 183 local source/title/output
  copies retain their accepted source-tree hashes.
- Full advisory Sentinel after generation: Fusionpunk **0/0/80/0**, all45 sources
  evaluated; Investing **0/0/7/0**, all16 sources evaluated. The minor English
  findings retain source codes/brands/intentional tokens, not a semantic certificate.
- Composite publish gates: two-book `publish:verify` generated both intended
  ranges, passed its shared ch001-ch016 gate, lint and a **776-page** build.
  Separate full-range Sentinel above covers Fusionpunk ch017-ch045 as well.
  The combined command timed out during smoke; the standalone smoke was then
  rerun to completion and passed, with zero unexpected console errors.
- Generator regressions **7/7**, persisted-reader regressions **5/5**, root tests
  **91/91**, Worker envelope tests **11/11**, DSE pipeline suite and governance pass.
  Initial pre-generation governance mismatch and Windows console encoding failure
  were resolved by generation and the documented UTF-8 invocation, not gate edits.
- Independent browser comparison: every rendered paragraph matches generated
  Markdown in five chapters per novel, at both 1440px and 390px. Samples:
  Fusionpunk 1/13/28/41/45; Investing 1/4/8/15/16. Titles, Code labels, final-next
  navigation and width checks pass. Excluded Fusionpunk46 and Investing17/21/56
  return404. Screenshot inspection confirms readable desktop/mobile output.

## Preservation and limits

The six unrelated books and legacy/default reader retain **982 existing snapshot
files byte-for-byte**. All forty previously public Fusionpunk chapter files remain
identical to their canonical Git blobs; only checkout CRLF was regenerated as LF.
Only its manifest and the aggregate library/import report intentionally change.
Historical Lean/Pipe labels are not rewritten. No reader code, provider route,
validator, threshold, synopsis, cover, raw corpus or run evidence is published.

Browser evidence uses the declared hermetic Playwright Chromium surface, not
every browser. Green invariants do not establish general semantic truth. Local
raw/title/output evidence remains ignored; the versioned reader snapshot, not a
reproducible translation corpus, is what a clean checkout can build.

**Not yet claimed:** merged/default-branch CI, deployment or live availability of
the interim additions. Those require owner-approved landing and exact merged-SHA
CI plus actual live verification. Record only the five new Fusionpunk and sixteen
new Investing first-publication IDs after that evidence exists; do not recount the
unchanged first forty or regeneration as new exposure.
