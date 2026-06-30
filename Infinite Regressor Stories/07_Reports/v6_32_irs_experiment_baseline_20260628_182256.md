# V6.32 IRS Experiment Baseline

- Created: 2026-06-28T18:22:56.837452+00:00
- Seed: 632
- In-sample: ch009, ch018, ch019, ch004, ch020, ch003, ch005, ch006, ch007, ch008
- Out-of-sample: ch021, ch023, ch026, ch032, ch034, ch035, ch038, ch040, ch044, ch055

## Baseline Ledger Metrics

- Records: 364
- Current failed QA blocks: ch019-block-002
- Historical failed blocks: 16
- Provider failures: {'openrouter_reasoning:qa': 12, 'openrouter:refining': 10}

## Sample Risk Table

| chapter | risk | blocks | max words | reasons | title |
| --- | ---: | ---: | ---: | --- | --- |
| ch009 | 12 | 2 | 1500 | zalgo_or_distorted_sound, large_block, footnotes, bracket_messages, system_or_lore_terms | Chapter 9 - The Determinist ⅠⅠ |
| ch018 | 12 | 2 | 1497 | zalgo_or_distorted_sound, large_block, footnotes, bracket_messages, system_or_lore_terms | Chapter 18 - The Companion I |
| ch019 | 12 | 2 | 1498 | zalgo_or_distorted_sound, large_block, footnotes, bracket_messages, system_or_lore_terms | Chapter 19 - The Companion II |
| ch004 | 10 | 3 | 1497 | large_block, many_blocks, footnotes, bracket_messages, system_or_lore_terms | Chapter 4 - The Observer II |
| ch020 | 10 | 3 | 1491 | large_block, many_blocks, footnotes, bracket_messages, system_or_lore_terms | Chapter 20 - The Companion III |
| ch003 | 8 | 2 | 1478 | large_block, footnotes, bracket_messages, system_or_lore_terms | Chapter 3 - The Observer I |
| ch005 | 8 | 2 | 1492 | large_block, footnotes, bracket_messages, system_or_lore_terms | Chapter 5 - The Hero |
| ch006 | 8 | 2 | 1495 | large_block, footnotes, bracket_messages, system_or_lore_terms | Chapter 6 - The Admin Ⅰ |
| ch007 | 8 | 2 | 1500 | large_block, footnotes, bracket_messages, system_or_lore_terms | Chapter 7 - The Admin II |
| ch008 | 8 | 2 | 1488 | large_block, footnotes, bracket_messages, system_or_lore_terms | Chapter 8 - The Determinist Ⅰ |
| ch021 | 9 | 2 | 1494 | large_block, footnotes, bracket_messages, system_or_lore_terms, english_title_sidecar_missing | Chapter 21 - The Reader I |
| ch023 | 9 | 2 | 1495 | large_block, footnotes, bracket_messages, system_or_lore_terms, english_title_sidecar_missing | Chapter 23 - The Reader III |
| ch026 | 15 | 3 | 1500 | zalgo_or_distorted_sound, large_block, many_blocks, footnotes, bracket_messages, system_or_lore_terms, english_title_sidecar_missing | Chapter 26 - The Prophet III |
| ch032 | 9 | 2 | 1492 | large_block, footnotes, bracket_messages, system_or_lore_terms, english_title_sidecar_missing | Chapter 32 - The Creator II |
| ch034 | 9 | 2 | 1495 | large_block, footnotes, bracket_messages, system_or_lore_terms, english_title_sidecar_missing | Chapter 34 - The Taxpayer I |
| ch035 | 9 | 2 | 1489 | large_block, footnotes, bracket_messages, system_or_lore_terms, english_title_sidecar_missing | Chapter 35 - The Taxpayer II |
| ch038 | 9 | 2 | 1500 | large_block, footnotes, bracket_messages, system_or_lore_terms, english_title_sidecar_missing | Chapter 38 - Rich Bond III |
| ch040 | 11 | 3 | 1498 | large_block, many_blocks, footnotes, bracket_messages, system_or_lore_terms, english_title_sidecar_missing | Chapter 40 - Observer II |
| ch044 | 9 | 2 | 1500 | large_block, footnotes, bracket_messages, system_or_lore_terms, english_title_sidecar_missing | Chapter 44 - Returnee I |
| ch055 | 9 | 2 | 1494 | large_block, footnotes, bracket_messages, system_or_lore_terms, english_title_sidecar_missing | Chapter 55 - Ruler II |

## Gate

- This report is read-only and does not call providers.
- Production scaling remains blocked until in-sample and out-of-sample experiment gates pass.
