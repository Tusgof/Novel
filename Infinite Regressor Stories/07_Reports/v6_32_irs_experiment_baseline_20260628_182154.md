# V6.32 IRS Experiment Baseline

- Created: 2026-06-28T18:21:54.512372+00:00
- Seed: 632
- In-sample: ch001, ch002, ch003, ch004, ch005, ch006, ch007, ch008, ch009, ch010
- Out-of-sample: ch021, ch023, ch026, ch032, ch034, ch035, ch038, ch040, ch044, ch055

## Baseline Ledger Metrics

- Records: 364
- Current failed QA blocks: ch019-block-002
- Historical failed blocks: 16
- Provider failures: {'openrouter_reasoning:qa': 12, 'openrouter:refining': 10}

## Sample Risk Table

| chapter | risk | blocks | max words | reasons | title |
| --- | ---: | ---: | ---: | --- | --- |
| ch001 | 0 | 0 | 0 | - | Chapter 1 - The Partner Ⅰ |
| ch002 | 0 | 0 | 0 | - | Chapter 2 - The Partner ⅠⅠ |
| ch003 | 0 | 0 | 0 | - | Chapter 3 - The Observer I |
| ch004 | 0 | 0 | 0 | - | Chapter 4 - The Observer II |
| ch005 | 0 | 0 | 0 | - | Chapter 5 - The Hero |
| ch006 | 0 | 0 | 0 | - | Chapter 6 - The Admin Ⅰ |
| ch007 | 0 | 0 | 0 | - | Chapter 7 - The Admin II |
| ch008 | 0 | 0 | 0 | - | Chapter 8 - The Determinist Ⅰ |
| ch009 | 0 | 0 | 0 | - | Chapter 9 - The Determinist ⅠⅠ |
| ch010 | 0 | 0 | 0 | - | Chapter 10 - The Troublemaker Ⅰ |
| ch021 | 1 | 0 | 0 | english_title_sidecar_missing | Chapter 21 - The Reader I |
| ch023 | 1 | 0 | 0 | english_title_sidecar_missing | Chapter 23 - The Reader III |
| ch026 | 1 | 0 | 0 | english_title_sidecar_missing | Chapter 26 - The Prophet III |
| ch032 | 1 | 0 | 0 | english_title_sidecar_missing | Chapter 32 - The Creator II |
| ch034 | 1 | 0 | 0 | english_title_sidecar_missing | Chapter 34 - The Taxpayer I |
| ch035 | 1 | 0 | 0 | english_title_sidecar_missing | Chapter 35 - The Taxpayer II |
| ch038 | 1 | 0 | 0 | english_title_sidecar_missing | Chapter 38 - Rich Bond III |
| ch040 | 1 | 0 | 0 | english_title_sidecar_missing | Chapter 40 - Observer II |
| ch044 | 1 | 0 | 0 | english_title_sidecar_missing | Chapter 44 - Returnee I |
| ch055 | 1 | 0 | 0 | english_title_sidecar_missing | Chapter 55 - Ruler II |

## Gate

- This report is read-only and does not call providers.
- Production scaling remains blocked until in-sample and out-of-sample experiment gates pass.
