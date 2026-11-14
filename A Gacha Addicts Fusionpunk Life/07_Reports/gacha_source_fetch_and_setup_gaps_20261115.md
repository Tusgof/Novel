# Source fetch and setup-gap fixes — 2026-11-15

Owner authorized fetching this novel through the existing `wetriedtls` adapter.
This report records the fetch, the three defects it exposed, and where each fix
now lives.

## Fetch result

- `ch001-ch040` fetched to `03_Raw/chXXX/source.json` through the explicit
  `--config` of this vault.
- 40/40 requests succeeded, 0 failures, 0 missing, 0 duplicates.
- 529,143 characters total; 13,228 average per chapter (10,651-15,943).
- Every `title` equals the real page heading, for example
  `Chapter 40: Premium Fever! (2)`. No generic `Chapter N` titles remain.
- No encoding damage, no CJK/Hangul body text, no promotional footer residue.
- `ch007` carries one 3-character Hangul token inside an explicit `Footnotes:`
  block explaining a wordplay in `변호사`; that is a translator note, not prose,
  and stays distinguishable per `LANGUAGE_PLAYBOOK.md`.
- `03_Raw`, `04_Work`, `05_Output`, and `06_Logs` are git-ignored at the
  workspace root, so no source corpus can be committed.

## Defect 1 — adapter did not recognise the current chapter heading

The site prints the chapter number and title on one line
(`Chapter 12: The Wastrel's Reward`), while the adapter required the paragraph to
match `Chapter N` exactly, so extraction failed closed.

- Fix: `_CHAPTER_MARKER_RE` accepts an optional inline title.
- Prevention: `test_wetriedtls_adapter.py`.

## Defect 2 — a generic manifest title discarded the real chapter title

`build_manifest()` synthesises `Chapter {n}` because the TOC carries no titles,
and `_derive_title_from_body_if_generic()` only understood a separator-plus-subtitle
layout, so the real title was lost even though it was present in the body.

- Fix: the helper now also accepts the inline `Chapter N: Title` heading and keeps
  the full heading line. A neighbouring number (`Chapter 120` for `Chapter 12`)
  is rejected.
- Prevention: `test_wetriedtls_adapter.py` (`FetchTitleDerivationTests`).

## Defect 3 — source state existed only as prose

The vault was scaffolded as "source-pending", but nothing machine-checkable held
that state: `NOVEL_PROFILE.yaml` had no state field, and `preflight` only checked
that the `03_Raw` directory existed. Nothing flipped when the source arrived, so
the README and the 2026-11-08 checkpoint would have kept claiming an empty
import mode after a real fetch.

- Fix: `NOVEL_PROFILE.yaml` gains `setup.source_state` with the values `pending`,
  `fetched`, and `validated`. `initialize_novel_project()` writes `pending`.
- Fix: `preflight` derives the actual state from `03_Raw/ch*/source.json` and
  warns when it contradicts the declared state. Vaults without the field report
  `unset` and are not checked, so no existing novel changes behaviour.
- Prevention: `test_source_state_readiness.py`.
- This vault now declares `source_state: fetched`.

## Related defect found while reading the scaffold code

`initialize_novel_project()` fell back to the template novel's `source.adapter`
when no `--adapter` was given, so a new vault could silently inherit a sibling
novel's source site (for example the Deep Sea Embers adapter). That contradicts
the non-negotiable boundary that no command silently falls back to another novel,
and `--adapter ''` could not clear it because the empty string was falsy.

- Fix: the adapter is no longer inherited; an unnamed adapter stays empty
  (import-only).
- Prevention: `test_workspace_routing.py` asserts that scaffolding without an
  adapter yields `source.adapter: ''` and that an explicit adapter is recorded.
- This vault now pins `source.adapter: wetriedtls` explicitly.

## Verification

- `python -m unittest test_wetriedtls_adapter test_source_state_readiness` — 15/15.
- `python -m unittest test_workspace_routing test_xszj_adapter test_opencode_provider test_kit_adoption` — 41/41.
- `python test_translation.py` from `Deep Sea Embers/` — all tests passed.
- New modules added to the `tests` workflow so the coverage runs in CI.

## Not claimed

Glossary approval, Thai title sidecars, the `ch001-ch003` pilot, provider-backed
translation, publication, and reader registration are all still pending. No
translated chapter exists for this novel.
