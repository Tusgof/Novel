# Source fetch ch041-ch082 — 2026-11-15

Owner requested `ch041-ch100` after the first batch stopped at `ch040`.

## Result

- `ch041-ch082` fetched: 42/42 successful, 0 failures.
- Vault now holds `ch001-ch082`, 82 chapters, no gaps, 1,055,669 characters total.
- New range: 526,526 characters, 10,094-14,651 per chapter, average 12,536.
- Titles: 0 generic `Chapter N`, 0 mismatches against the page heading, 0 duplicates.
- No encoding damage, no promotional footer residue.

## ch083-ch100 are paywalled, not broken

All 18 requests returned HTTP 200 but the adapter refused to extract:

```
ValueError: WetriedtlsAdapter could not find a chapter marker in the page payload
```

Page comparison shows why:

| page | bytes | body `<p>` tags | paywall markers |
| --- | --- | --- | --- |
| chapter-82 | 223,377 | 515 | none |
| chapter-83 | 55,672 | 13 | `unlock` x3, `coin` x7 |
| chapter-100 | 55,690 | 13 | `unlock` x3, `coin` x7 |

The site serves a locked shell for paid chapters. The adapter's fail-closed
behaviour is correct: it must not emit body text it cannot see. 82 is the free
ceiling of this source, so the remaining chapters need another legally available
source or supplied files (`fetch --input-file`, or
`99_Adhoc_Scripts/import_sources.py` for a folder).

## Reviewed and accepted as source style

A standalone `"?????"` dialogue line appears once each in `ch055`, `ch059`, and
`ch082`, always as a wordless confusion reaction inside quotes. This is an authored
device rather than placeholder corruption, which would replace a word mid-sentence.
A translation must render it consistently.

`ch007` still carries one Hangul token inside an explicit `Footnotes:` block; that
remains a translator note, not prose.

## Docs updated

`README.md`, `NOVEL_PROFILE.yaml` (`source_plan.chapter_range`), and
`RESEARCH_PROFILE.yaml` notes now state the `ch001-ch082` free scope and why it ends
there, so the vault does not drift back to claiming a 40-chapter scope.

No translation, glossary approval, title sidecar, or publication was performed in
this batch.
