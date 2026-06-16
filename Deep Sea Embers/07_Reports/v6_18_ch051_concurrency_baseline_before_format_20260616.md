# Concurrency Benchmark Report - v6-18-benchmark-ch051-v1

Read-only V6.18A benchmark planning report. It does not enable parallel runtime, execute providers, edit ledger, or change artifacts.

## Benchmark Summary
| stage | provider | configured limit | duration records | failed | projected saved seconds | projected reduction % | decision | next action |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| refining | openrouter | 2 | 0 | 0 | 0.00 | 0.0 | not_ready | collect cleaner timing data or review failed records |
| translating | openrouter | 2 | 0 | 0 | 0.00 | 0.0 | not_ready | collect cleaner timing data or review failed records |

## Execution Policy
| stage | configured limit | effective limit | concurrency enabled |
| --- | ---: | ---: | --- |
| formatting | 2 | 1 | false |
| qa | 1 | 1 | false |
| refining | 2 | 1 | false |
| translating | 2 | 1 | false |

## Recommendations
| stage | provider | duration records | average seconds | failed | recommendation | confidence |
| --- | --- | ---: | ---: | ---: | --- | --- |
| refining | openrouter | 0 | n/a | 0 | collect more timing metadata before concurrency | low |
| translating | openrouter | 0 | n/a | 0 | collect more timing metadata before concurrency | low |

## Simulation
| stage | provider | timing records | configured limit | sequential seconds | projected seconds | estimated saved seconds | reduction % | note |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| formatting | none | 0 | 2 | 0.00 | 0.00 | 0.00 | 0.0 | insufficient completed timing records |
| qa | openrouter | 0 | 1 | 0.00 | 0.00 | 0.00 | 0.0 | configured limit is sequential |
| qa | openrouter_reasoning | 0 | 1 | 0.00 | 0.00 | 0.00 | 0.0 | configured limit is sequential |
| qa | qwen | 0 | 1 | 0.00 | 0.00 | 0.00 | 0.0 | configured limit is sequential |
| refining | openrouter | 0 | 2 | 0.00 | 0.00 | 0.00 | 0.0 | insufficient completed timing records |
| translating | openrouter | 0 | 2 | 0.00 | 0.00 | 0.00 | 0.0 | insufficient completed timing records |

## Safety Notes
- This report is not approval to set `execution.concurrency_enabled: true`.
- Glossary approval remains sequential and human-gated.
- QA and AI formatting must remain enabled in any benchmark.
- Stop on first hard failure, provider failure spike, command_too_long, or final-output guardrail regression.
