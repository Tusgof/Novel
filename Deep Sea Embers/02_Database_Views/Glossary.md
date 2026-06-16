# Glossary View

```dataview
TABLE file.link AS Term, original_term, thai_term, category, status, source_language, aliases, novel
FROM "01_Glossary"
WHERE type = "glossary-term"
SORT status ASC, file.name ASC
```

## Field Expectations

- `original_term` is the source-language term.
- `thai_term` is the approved Thai rendering.
- `status` uses `proposed`, `approved`, or `deprecated`.
- `aliases` stores scan-time variants that should resolve to the same note.
- `novel` identifies the story this glossary entry belongs to.
