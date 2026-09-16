# Re:Zero ch005-ch010 Glossary Gate

Date: 2026-09-17

Runs:

- `rezero-ch005-production-v1`
- `rezero-ch006-production-v1`
- `rezero-ch007-production-v1`
- `rezero-ch008-production-v1`
- `rezero-ch009-production-v1`
- `rezero-ch010-production-v1`

## Source And Scan Validation

- Raw source and title sidecars for `ch005-ch010` were prepared and validated before this review.
- Every run is chapter-isolated and has only a completed `glossary_scanned` record before approval.
- Reviewed candidate counts are 59, 35, 42, 50, 61, and 81 respectively.
- No translate, refine, QA, format, final-output, publication, commit, or push action was part of this gate.

## Inspector Decision

Approved durable additions:

- Story terms and places: `Forbidden Library`, `Roswaal Estate`, `The Warden`, `The Red Ogre Who Cried`, `Memory Snow`, `Operation Hot Springs`, and `The Sickness Called Despair`.
- Canon objects, creatures, and concepts: `Morning Star`, `Holy Dragon`, `Ulgarm Mabeast`, `Imperial Knights`, `Dragon Stone`, `Heavenly Dragon Sword`, `Demi-Human`, `Unseen Hand`, and `The Ordeal`.
- Characters and stable identities: `Mother Fortuna`, `Cromwell`, `Miklotov`, `Hetaro`, `House Karsten`, `Patrasche`, `Petelgeuse Romanee-Conti`, and `Father Geuse`.
- Existing-note aliases: `Irlam`, `Bubby`, `Preistella`, `Julius Juukilous`, `Julius Euclius`, `Petra Lyte`, `Priscilla Barialle`, `Barielle`, `Barialle`, `Lia`, and `Beako`.

The approved Thai values reuse established output wording where `ch001-ch004` already supplied evidence. Canon spelling aliases normalize source typos without preserving the typo in Thai.

`Sloth` and `Gluttony` are not added as aliases to the full Sin Archbishop titles because the source also uses them contextually for expeditions, incidents, and the represented sins. They remain context-sensitive while the existing full titles stay authoritative.

Rejected candidates are honorific-only combinations, generic role labels, media metadata without durable translation value, shouted sentences, dialogue fragments, source prose accidentally extracted as names, and obvious extractor noise such as `Had Betty`, `Does Ram`, and `Both Rem`.

## Approval

This decision authorizes one `glossary_approved` ledger record for each listed chapter-isolated run after its chapter scan artifact is copied into the matching run-specific batch scope. Glossary mutation is frozen after these commits until the parallel body window closes.
