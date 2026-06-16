# Run Plan Report - deep-sea-embers-retranslate-ch001-ch050-v2

## Summary
- read_only: yes
- preflight_status: degraded
- current_failed_blocks: none
- manual_actions: none
- recommended_batch_size: 1-3 chapters
- recommended_checkpoint: next bounded range after ch050

## Suggested Commands
- `novel-pipeline --config "D:\Fogust\Workspace\Novel\Deep Sea Embers\.system\config.yaml" status --run-id deep-sea-embers-retranslate-ch001-ch050-v2`
- `novel-pipeline --config "D:\Fogust\Workspace\Novel\Deep Sea Embers\.system\config.yaml" report checkpoint --run-id deep-sea-embers-retranslate-ch001-ch050-v2`
- `novel-pipeline --config "D:\Fogust\Workspace\Novel\Deep Sea Embers\.system\config.yaml" report provider-usage --run-id deep-sea-embers-retranslate-ch001-ch050-v2`
- `novel-pipeline --config "D:\Fogust\Workspace\Novel\Deep Sea Embers\.system\config.yaml" resume --run-id deep-sea-embers-retranslate-ch001-ch050-v2 --manual-action-mode stop`

## Provider Readiness
| provider | status | stages | transport |
| --- | --- | --- | --- |
| claude | ready | term_suggestion:fallback | stdin |
| codex | ready | fetch, literal_translation:fallback, project_setup, qa_judge:fallback, refinement:fallback, term_extraction:fallback | stdin |
| openrouter | ready | formatting, formatting:fallback, literal_translation, literal_translation:fallback, qa_judge:fallback, refinement, refinement:fallback, refinement:fallback, term_extraction, term_extraction:fallback, term_suggestion, term_suggestion:fallback | stdin |
| openrouter_reasoning | ready | qa_judge | stdin |
| qwen | ready | qa_judge:fallback, refinement:fallback | stdin |

## Routing And Fallbacks
| stage | provider | model | fallbacks | timeout |
| --- | --- | --- | --- | --- |
| fetch | codex | gpt-5.4 | none | default |
| formatting | openrouter | deepseek/deepseek-v4-flash | openrouter/google/gemini-3-flash-preview | default |
| literal_translation | openrouter | google/gemini-3-flash-preview | openrouter/deepseek/deepseek-v4-flash, codex/gpt-5.4 | default |
| project_setup | codex | gpt-5.4 | none | default |
| qa_judge | openrouter_reasoning | deepseek/deepseek-v4-flash | qwen/deepseek-reasoner, openrouter/deepseek/deepseek-v4-pro, codex/gpt-5.4 | default |
| refinement | openrouter | deepseek/deepseek-v4-flash | openrouter/google/gemini-3-flash-preview, openrouter/anthropic/claude-sonnet-4.6, codex/gpt-5.4, qwen/deepseek-reasoner | default |
| term_extraction | openrouter | google/gemini-3-flash-preview | openrouter/deepseek/deepseek-v4-flash, codex/gpt-5.4 | 120.0 |
| term_suggestion | openrouter | deepseek/deepseek-v4-flash | openrouter/google/gemini-3-flash-preview, claude/sonnet | 120.0 |

## Recent Failures
| block | stage | provider | status | message |
| --- | --- | --- | --- | --- |
| ch020-block-005 | refining | openrouter | failed | Provider 'openrouter' returned unusable output (nonzero_exit). OpenRouter shim error after 24.06s: OpenRouter returned an empty assistant message. |
| ch026-block-004 | qa | local | hard_fail |  |
| ch029-block-005 | qa | local | hard_fail |  |
| ch037-block-002 | qa | local | hard_fail |  |
| ch041-block-002 | refining | openrouter | failed | Provider 'openrouter' returned unusable output (nonzero_exit). OpenRouter shim error after 5.72s: <urlopen error [WinError 10054] An existing connection was forcibly closed by the remote host> |
| ch041-block-002 | refining | openrouter | failed | Provider 'openrouter' returned unusable output (nonzero_exit). OpenRouter shim error after 26.53s: [WinError 10054] An existing connection was forcibly closed by the remote host |
| ch043-block-006 | formatting | local | failed |  |
| ch044-block-001 | qa | local | hard_fail |  |

## Cache Readiness
| stage | completed | artifact exists | input hash | output hash | hash-cache ready |
| --- | ---: | ---: | ---: | ---: | ---: |
| translating | 266 | 266 | 266 | 266 | 266 |
| refining | 266 | 266 | 214 | 266 | 214 |
| qa | 266 | 266 | 0 | 0 | 0 |
| formatting | 266 | 266 | 0 | 266 | 0 |

## Cache Policy
| mode | runtime skip | stages | rule |
| --- | --- | --- | --- |
| report_only | false | title_translation, term_suggestion, translating | skip only when stage input hash, output hash, and artifact validation match |

## Speed Savings Estimate
| stage | cache-ready artifacts | average seconds | estimated seconds saved | confidence | note |
| --- | ---: | ---: | ---: | --- | --- |
| translating | 266 | n/a | n/a | low | insufficient clean timing baseline |
| refining | 214 | n/a | n/a | low | insufficient clean timing baseline |
| qa | 0 | n/a | n/a | low | insufficient clean timing baseline |
| formatting | 0 | 21.90 | 0.00 | low | read-only estimate; runtime cache skip is not enabled |

## Timing Baseline
| stage | provider | records | completed | failed | duration records | total seconds | average seconds |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| completed | local | 267 | 267 | 0 | 0 | 0.00 | n/a |
| fetched | local | 50 | 50 | 0 | 0 | 0.00 | n/a |
| formatting | local | 7 | 4 | 3 | 0 | 0.00 | n/a |
| formatting | openrouter | 268 | 268 | 0 | 268 | 5868.58 | 21.90 |
| glossary_approved | local | 50 | 50 | 0 | 0 | 0.00 | n/a |
| glossary_scanned | local | 50 | 50 | 0 | 0 | 0.00 | n/a |
| qa | local | 5 | 0 | 5 | 0 | 0.00 | n/a |
| qa | openrouter | 272 | 271 | 1 | 0 | 0.00 | n/a |
| refining | codex | 1 | 1 | 0 | 0 | 0.00 | n/a |
| refining | openrouter | 346 | 339 | 7 | 7 | 136.03 | 19.43 |
| translating | codex | 1 | 1 | 0 | 0 | 0.00 | n/a |
| translating | openrouter | 268 | 266 | 2 | 2 | 24.20 | 12.10 |

## Concurrency Benchmark Recommendations
| stage | provider | duration records | average seconds | failed | recommendation | confidence |
| --- | --- | ---: | ---: | ---: | --- | --- |
| formatting | local | 0 | n/a | 3 | keep sequential until failures are reviewed | low |
| formatting | openrouter | 268 | 21.90 | 0 | benchmark concurrency=2 on a small approved range | medium |
| refining | codex | 0 | n/a | 0 | collect more timing metadata before concurrency | low |
| refining | openrouter | 7 | 19.43 | 7 | keep sequential until failures are reviewed | low |
| translating | codex | 0 | n/a | 0 | collect more timing metadata before concurrency | low |
| translating | openrouter | 2 | 12.10 | 2 | keep sequential until failures are reviewed | low |

## Concurrency Simulation
| stage | provider | timing records | configured limit | sequential seconds | projected seconds | estimated saved seconds | reduction % | note |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| formatting | local | 0 | 2 | 0.00 | 0.00 | 0.00 | 0.0 | simulation withheld because stage/provider has failed records |
| formatting | openrouter | 268 | 2 | 5868.58 | 3955.88 | 1912.71 | 32.6 | simulation only; runtime remains sequential |
| qa | local | 0 | 1 | 0.00 | 0.00 | 0.00 | 0.0 | simulation withheld because stage/provider has failed records |
| qa | openrouter | 0 | 1 | 0.00 | 0.00 | 0.00 | 0.0 | simulation withheld because stage/provider has failed records |
| refining | codex | 0 | 2 | 0.00 | 0.00 | 0.00 | 0.0 | insufficient completed timing records |
| refining | openrouter | 0 | 2 | 0.00 | 0.00 | 0.00 | 0.0 | simulation withheld because stage/provider has failed records |
| translating | codex | 0 | 2 | 0.00 | 0.00 | 0.00 | 0.0 | insufficient completed timing records |
| translating | openrouter | 0 | 2 | 0.00 | 0.00 | 0.00 | 0.0 | simulation withheld because stage/provider has failed records |

## Execution Policy
| stage | configured limit | effective limit | concurrency enabled |
| --- | ---: | ---: | --- |
| formatting | 2 | 1 | false |
| qa | 1 | 1 | false |
| refining | 2 | 1 | false |
| translating | 2 | 1 | false |

## Benchmark Scope Plan
| stage | provider | target limit | scope | prerequisite | stop condition |
| --- | --- | ---: | --- | --- | --- |
| formatting | openrouter | 2 | next approved 1-chapter bounded range after ch050 | user-approved scan/glossary gate and no current failed blocks | first provider failure, QA hard-fail, formatting validation failure, or scope expansion |

## Guardrail Policy
| guardrail | mode | runtime blocking | threshold |
| --- | --- | --- | --- |
| pre_qa | report_only | false | dense paragraph warning >900 chars |

## Pre-QA Guardrail Preview
- report_only: yes
- refined_artifacts_checked: 266
- missing_refined_artifacts: 0
- hard_error_blocks: 0
- warning_blocks: 3

| block | hard errors | warnings | artifact |
| --- | --- | --- | --- |
| ch034-block-004 | none | dense_paragraph:1667 | D:\Fogust\Workspace\Novel\Deep Sea Embers\04_Work\ch034\ch034-block-004.refined.json |
| ch043-block-001 | none | dense_paragraph:1010 | D:\Fogust\Workspace\Novel\Deep Sea Embers\04_Work\ch043\ch043-block-001.refined.json |
| ch043-block-006 | none | quote-only line 7 | D:\Fogust\Workspace\Novel\Deep Sea Embers\04_Work\ch043\ch043-block-006.refined.json |

## Speed-Safety Notes
- glossary approval remains human-gated and sequential
- QA and AI formatting stay enabled; this report does not replace either gate
- cache readiness is report-only; execution still uses existing ledger skip behavior
- pre-QA guardrail preview is report-only; it does not block or skip AI QA yet
- keep risky stages sequential until a benchmark proves stability
- use bounded resume/checkpoints rather than open-ended production runs
