# Re:Zero ch004 Glossary Gate

Date: 2026-09-16
Run: `rezero-ch004-production-v1`

## Source Validation

- `ch004/source.json` is the previously validated full raw chapter and contains no anti-bot challenge marker.
- The chapter was scanned under its chapter-isolated production run before body translation.

## Inspector Decision

The scan returned 47 candidates. Two durable canon terms are added:

- `Alram Village` is normalized as the alias of `Arlam Village` -> `หมู่บ้านอาร์แลม`.
- `Door Crossing` -> `การข้ามประตู` as Beatrice's named ability.

Existing glossary entries already cover the durable names and titles in this chapter, including Subaru, Crusch, Garfiel, Roswaal, Sword Saint, Beatrice, Emilia, Ram, Rem, Otto, and Barusu. Honorific combinations remain contextual aliases and do not become separate Thai terms. `Styx Helix` and title-card/media labels remain source media names. The remaining candidates are dialogue fragments, temporary forms of address, generic descriptions, shout text, or extraction noise and are rejected for durable glossary storage.

## Approval

This reviewed decision authorizes `glossary_approved` for `ch004` in `rezero-ch004-production-v1`. Body translation may begin after that ledger commit.
