# Immortality System Glossary Decisions: ch011-ch015

## Scope

- Run: `immortality-system-ch011-ch015-v1`
- Chapters: `ch011-ch015`
- Rescan coverage: 59 candidates after raising the five-chapter scan budget from 8 to 32 provider calls.

## Decision

- Approve stable character names, named places, sect ranks, cultivation realms, formations, materials, and recurring supernatural concepts.
- Reject generic descriptions, ordinary nouns, scanner fragments, and short forms already covered by a more precise term.
- Keep simplified/traditional source-script forms aligned to the same Thai rendering where both occur in fetched source.

## Prevention

The previous 8-call cap covered only the opening blocks of a five-chapter batch and missed later-chapter terms. Immortality System now reserves 32 term-extraction calls per scan, with regression coverage requiring at least 20 calls for the default five-chapter batch.

Machine-readable decisions are recorded in `glossary_decisions_immortality-system-ch011-ch015-v1.json`.
