# Two Code novels: original covers and live1–60 verified

**Measured:** both books serve exactly ch001–ch060 with their new original covers
on [MoonRead](https://novel-pink-nu.vercel.app). The owner's instruction was to
create both covers first, then merge and update the real site. That conditional
approval was explicit; no agent self-approval was used.

## Landing and actual production identity

- [PR22](https://github.com/Tusgof/Novel/pull/22) rebase-merged at
  `2026-11-16T15:18:07Z` to `7349baef3c07b8c908eb6b993266e0a6ee05b757`.
- The tested cover head was `9662c3331b8e7a7dac82d3011c54c854feec10ec`;
  [head tests43894467282](https://github.com/Tusgof/Novel/actions/runs/43894467282)
  and Vercel checks passed. The merged tree is identical to that tested tree.
- [Default-branch tests43894858247](https://github.com/Tusgof/Novel/actions/runs/43894858247)
  passed for the exact merged SHA, not merely a previous/latest run.
- Existing Git integration automatically deployed that SHA as production
  `dpl_B1Cj9AFgCEvyBJGGxLuiZTWBAekn`, observed `READY` with `aliasError:null`.
  A lookup of the actual public hostname, not only a deployment listing, resolves
  `novel-pink-nu.vercel.app` to that deployment and exact SHA.
- No manual deploy, project/config/account change or new credential was needed.
  Rollback baseline `dpl_8QKKuVU6wmXwtnZhJBKyZ4tVsFhX` served
  `aab34c12f4378de0d333da3d60fb3b146416cd0b`. Own remote release branch removed
  after merge; local evidence and unrelated translation WIP preserved.

## Actual public-reader checks

The unauthenticated live run began at `2026-11-16T15:20:50.788Z` and completed
successfully, using fresh task-owned Playwright Chromium148.0.7778.96 rather than
a signed-in profile. Screenshots/extracted browser evidence stay outside Git.

- All120 HTTP chapter routes returned200. Every one of18,486 rendered paragraphs,
  chapter headings and Code labels matches accepted generated Markdown.
- All24 hydrated desktop/mobile samples passed at1440px/390px: Gacha
  1/15/30/46/56/60 and Investing1/15/30/38/57/60. Text and authored newline
  rendering are preserved; no horizontal overflow or unexpected console/page error.
- Four TOC checks each show exactly60 rows. Neither60page links to61, and both
  chapter61routes return404. There is no continuation beyond the owner's scope.
- Homepage cards and desktop/mobile book heroes display the actual new covers.
  Four live book-cover screenshots inspected; focal characters/coin/wheelchair
  remain legible, with readable hero text and no broken/cropped-away cover subject.
- Both public WebP assets returned200 and match exact local bytes:
  - Gacha139428bytes: `8940ae6d9c3a10b9e3f1094eaa1b1a9809e45bb16dc6a30926ae08756b570ffa`
  - Investing161390bytes: `2db8d0be873abff5a7f3dc4c568abf41ce14cedf4f19034129a75c86f5d479b3`

## Covers and preservation

Both original2:3 text-free PNGs, exact prompts and handoff notes are versioned in
`00_Assets/cover_art/20261116/`. The owner specifically requested OpenAI SDK
Responses/image_generation through existing codex-lb after the Images endpoint
failed. Responses succeeded with existing mainline `gpt-6.1-sol` and requested
tool model `gpt-image-2`, one completed image call per cover, automatic SDK retries0.
An unsupported optional-parameter400 was corrected before successful generation.
No shared skill, credential store, service config, account or billing setting was
changed. Dollar cost and remaining allowance are not proven by token usage.

Local cover-inclusive publish:verify passed8books/814available/0missing/0rejected,
Sentinel0/0/0/0 with120sources, lint,835-page build and eight-book smoke. Generator
7/7, reader6/6 (including actual multiline glyph positions), root91/91, envelope
11/11, DSE pipeline and governance passed. Doctor before/after landing remains
fail0/warn1/unverified0; the portability warning is pre-existing399files.

All120 accepted chapter files,61 old public chapters and982 unrelated/legacy
snapshot files are preserved. Cover integration leaves1102generated files and
all33reader-code files byte-identical;360 staged accepted-input hashes still match.
PR22 changes72paths, including exactly59new chapter files, two cover paths and
cover art/provenance. No reader code, raw/run corpus, provider/gate, source ceiling,
author, synopsis, story-ending status or unrelated book changed. Detailed local
acceptance and historical incident limits remain in
`two_books_code60_reader_candidate_20261116.md`.

## Exposure and limits

Only after this live verification, the ledger adds Gacha46–60 and Investing17–60:
59 distinct newly first-published IDs. The61 previously evidenced IDs are retained,
not counted again. Cover creation, regenerated manifests and the evidence-only
closeout are not additional publications. No reader-discovered incident is invented
from a passing test; historical ascertainment remains incomplete.

This proves the checked output/rendering/assets, not universal semantic fidelity.
Source/run evidence stays local; a clean checkout reproduces reader content and
cover assets, not the full translation corpus. Both translation Workers remain
stopped at60. The closeout changes only evidence and the publication ledger;
it does not regenerate content or authorize61+ translation.
