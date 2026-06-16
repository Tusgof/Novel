# Glossary by Category

```dataview
TABLE WITHOUT ID
  file.link AS Term,
  original_term AS Original,
  thai_term AS "Thai Term",
  status AS Status,
  first_seen_chapter AS "First Seen"
FROM "01_Glossary"
WHERE type = "glossary-term"
SORT category ASC, file.name ASC
GROUP BY category
```

## Categories

Standard categories used by the pipeline:
- `character` — named characters and their titles
- `location` — places, cities, realms
- `sect` — organizations, factions, sects
- `realm` — cultivation realms, power levels
- `item` — weapons, artifacts, treasures
- `technique` — skills, spells, martial arts
- `term` — general vocabulary, concepts
