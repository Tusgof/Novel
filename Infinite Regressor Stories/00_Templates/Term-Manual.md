---
type: glossary-term
original_term: <% tp.file.title %>
thai_term: <% await tp.system.prompt("Thai translation (leave empty to propose)") %>
status: proposed
aliases: []
source_language: <% await tp.system.suggester(["zh (Chinese)", "en (English)"], ["zh", "en"]) %>
category: <% await tp.system.suggester(["character", "location", "sect", "realm", "item", "technique", "term"], ["character", "location", "sect", "realm", "item", "technique", "term"]) %>
novel: deep-sea-embers
first_seen_chapter: <% await tp.system.prompt("First seen chapter ID (e.g. ch001)", "") %>
first_seen_block:
description: <% await tp.system.prompt("Short description") %>
related: []
approved_by:
approval_notes:
created_at: <% tp.date.now("YYYY-MM-DDTHH:mm:ss") %>
updated_at: <% tp.date.now("YYYY-MM-DDTHH:mm:ss") %>
---

## Summary

## Context Examples

## Translation Notes

## Related Terms

Use `[[linked terms]]` in the body when the note needs to point at another approved glossary entry.

## Runtime Contract

- `status = proposed` means the term still needs human approval.
- `status = approved` means the runtime can treat the term as canonical.
- `status = deprecated` means the term should stay searchable but should not be used for new translations.
- `aliases` should list source spellings or variant forms that the scanner may match.
- `first_seen_chapter` and `first_seen_block` record where the term was first discovered in the source text.
