# Checkpoint Report - rezero-ch004-production-v1

## Run Summary
- total_records: 64
- completed_blocks: ch004-block-001, ch004-block-002, ch004-block-003, ch004-block-004, ch004-block-005, ch004-block-006, ch004-block-007, ch004-block-008, ch004-block-009, ch004-block-010
- current_failed_blocks: none
- historical_failed_records: 5
- next_effective_action: none

## Manual Actions
- none

## Chapter Summary
| chapter | expected blocks | complete | failed | pending | output |
| --- | ---: | ---: | --- | --- | --- |
| ch004 | 10 | 10 | none | none | exists |

## Chapter Timing
| chapter | wall seconds | provider seconds | failed provider seconds | retry provider seconds | timed records | provider calls | retries | failures |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ch004 | 7964.85 | 4673.23 | 1776.49 | 925.13 | 50 | 51 | 3 | 5 |

## Stage And Provider Timing
| chapter | stage | provider | seconds |
| --- | --- | --- | ---: |
| ch004 | translating | openrouter | 536.95 |
| ch004 | refining | openrouter | 3563.19 |
| ch004 | qa | openrouter | 50.75 |
| ch004 | qa | openrouter_reasoning | 109.74 |
| ch004 | formatting | openrouter | 412.60 |

Provider time excludes local stages. Wall time includes waits and recovery gaps between the first and last timed record.

## Block Status
| block | next pending | records |
| --- | --- | ---: |
| ch004-block-001 | none | 5 |
| ch004-block-002 | none | 8 |
| ch004-block-003 | none | 5 |
| ch004-block-004 | none | 5 |
| ch004-block-005 | none | 8 |
| ch004-block-006 | none | 5 |
| ch004-block-007 | none | 6 |
| ch004-block-008 | none | 9 |
| ch004-block-009 | none | 5 |
| ch004-block-010 | none | 5 |
