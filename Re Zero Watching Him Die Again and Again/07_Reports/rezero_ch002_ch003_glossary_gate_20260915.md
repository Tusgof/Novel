# Re:Zero ch002-ch003 Glossary Gate

Date: 2026-09-15
Run: `rezero-ch002-ch003-production-v2`

## Source Validation

- `ch002`: 269,936 source characters, 46,635 whitespace-delimited words, no anti-bot marker.
- `ch003`: 176,686 source characters, 30,454 whitespace-delimited words, no anti-bot marker.
- Planned blocks at the 3,000-word limit: `ch002` 16 blocks and `ch003` 11 blocks.
- The earlier `v1` scan is rejected because its fetch phase replaced `ch002` with the 41-character message `Enable JavaScript and cookies to continue`.

## Candidate Review

The clean `v2` scan returned 109 candidates. Inspector review approved 27 durable canon names, titles, entities, organizations, and recurring concepts after an AI three-option term-suggestion pass:

- Characters: Ricardo, Frederica Baumann, Petra Leyte, Julius Juukulius, Mimi, Priscilla, Crusch, Otto Suwen, Felt, Felix, Barusu, Tivey, Rom, Wilhelm van Astrea, Elsa Granhiert, Puck, Al.
- Canon terms: Great Spirit, Dragon-drawn Carriage, Sword Demon, Hoshin Company, White Whale, Sloth Archbishop, Sleeping Beauty, Bowel Hunter, Jealous Witch, Priscilla Camp.
- Existing notes were extended only for source variants of Reinhard van Astrea and Sword Saint.

The remaining candidates are rejected for this gate. They are dialogue fragments, shout text, temporary forms of address/honorific combinations, generic prose, song/author-note metadata, or noisy multiword spans such as `THIS ISN'T RIGHT`, `Did Subaru`, `Lord Roswaal-sama`, and `Directors Cut`. They must be translated from context and must not enter the durable glossary.

## Prevention

- The FanFiction/Jina adapter now rejects known anti-bot challenge markers.
- This novel requires at least 1,000 extracted source characters before a web fetch can replace `source.json`.
- Production uses only `rezero-ch002-ch003-production-v2`; the contaminated `v1` run must never be resumed.

## Approval

The reviewed glossary is ready for non-interactive batch approval. Translation may begin only after `glossary_approved` is committed for both chapters in the `v2` ledger.
