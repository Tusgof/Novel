# Pending Terms

```dataview
TABLE file.link AS Term, original_term, category, source_language, novel, first_seen_chapter, first_seen_block, aliases
FROM "01_Glossary"
WHERE type = "glossary-term" AND status = "proposed"
SORT file.name ASC
```

## Review Contract

Only terms with `status = proposed` should appear here.
After approval, the runtime should update the same note to `status = approved` and remove it from this view automatically.
