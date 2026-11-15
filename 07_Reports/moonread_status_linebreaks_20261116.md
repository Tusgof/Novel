# MoonRead authored status-line breaks

## Report and measured cause

The reader reported that Fusionpunk ch039 status-window lines run together even
though the translation otherwise reads well. Expected: every authored status,
option and item-detail newline starts a new visible line, with long lines still
wrapping on mobile. No wording, number, effect or translation change is intended.

Live unauthenticated Playwright Chromium reproduction at1440px and390px confirms
the defect. The ten-line Premium Fever block retains its newline characters in
the published text, but computed `white-space` is `normal`: adjacent line-start
and preceding line-end glyphs share the same y-coordinate. The renderer parses
multiline groups into one paragraph and JSX keeps the characters; browser
whitespace processing then collapses them. This is presentation loss, not missing
translation data. Previous all-paragraph text comparisons could not detect it.

## Smallest correction and prevention

Set `.reader-paragraph` to `white-space: pre-line`. This preserves authored line
breaks while collapsing ordinary extra spaces and allowing long text to wrap.
Do not add blank paragraphs, HTML, special status heuristics or new translation
output. Existing font, emphasis, paragraph spacing and navigation are unchanged.

The new existing-suite reader regression measures real first/last glyph rects,
not just textContent or the CSS property. It covers the actual Gacha39 Premium
Fever/status and item-detail blocks and Investing15 personal status at desktop
and mobile widths, retaining exact text and rejecting horizontal overflow.
It **fails on the original build** at Gacha39 line2/1440px, matching the live bug.
Post-fix verification and landing status are recorded below when measured.

Static pattern inspection found100 candidate multiline system/item groups in
21 published Gacha and7 Investing chapters. Those are text-pattern candidates,
not independent visual confirmation of every page. The single reader-discovered
incident records confirmed ch039 against the original first40 publication cohort.
No new publication cohort or exposure is added for this renderer change.

## Scope and limits

- Isolated branch from main030a285; original translation Worker tree and all
  active frozen contexts remain untouched. Both translation tasks retain their
  separate bounded acceptance and publication boundaries.
- Medium-reasoning diagnosis and acceptance stay with main. Main-agent fallback
  handles the small mechanical edit because the restricted execution-worker has
  no verified safe native path to this external isolated worktree. No reader
  implementation subagent or alternate paid provider is used.
- Do not regenerate chapters: this is a CSS-only presentation repair over the
  accepted versioned snapshot. Run lint/build/smoke and reader regressions directly;
  `publish:verify` generation is intentionally skipped to keep all content bytes
  unchanged, not to bypass a failed source or quality gate.
- Browser evidence uses a fresh unsigned Chromium profile, public MoonRead and
  task-owned local server only. Screenshots/geometry stay outside the repository;
  no credential, service/account setting, translation route or gate changes.

## Verification status

- Before: live desktop/mobile failure reproduced; geometric regression red.
- After: the new geometry check passes for all three real status/item blocks at
  both1440px and390px. Independent Gacha39 probing confirms every authored break
  is visible with `pre-line`, left-aligned starts and no horizontal overflow;
  screenshot inspection confirms the result at both widths.
- Existing reader suite **6/6**, generator regressions **7/7**, root tests **91/91**,
  lint, **776-page build**, governance and the completed eight-book desktop/mobile
  smoke pass. The intentional404 check is separate from unexpected console errors,
  of which there are none. Existing themes/settings/emphasis/navigation still pass.
- All **1,047 versioned snapshot files** and the registry/ranges are unchanged.
  Existing incident/cohort entries are retained; one confirmed reader-layout
  incident is appended, with zero extra publication exposure.
- Public deployment: not yet claimed; owner approval is required for this new
  reader-code PR. Prior approval covered release/evidence only, not this code fix.
