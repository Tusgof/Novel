# Concurrency Benchmark Report - deep-sea-embers-retranslate-ch001-v1

Read-only V6.18A benchmark planning report. It does not enable parallel runtime, execute providers, edit ledger, or change artifacts.

## Benchmark Summary
| stage | provider | configured limit | duration records | failed | projected saved seconds | projected reduction % | decision | next action |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| formatting | local | 2 | 0 | 1 | 0.00 | 0.0 | not_ready | collect cleaner timing data or review failed records |
| formatting | qwen | 2 | 6 | 0 | 0.00 | 0.0 | not_ready | collect cleaner timing data or review failed records |
| refining | claude | 2 | 0 | 0 | 0.00 | 0.0 | not_ready | collect cleaner timing data or review failed records |
| translating | gemini | 2 | 0 | 0 | 0.00 | 0.0 | not_ready | collect cleaner timing data or review failed records |

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
| formatting | local | 0 | n/a | 1 | keep sequential until failures are reviewed | low |
| formatting | qwen | 6 | 14.15 | 0 | collect more timing metadata before concurrency | low |
| refining | claude | 0 | n/a | 0 | collect more timing metadata before concurrency | low |
| translating | gemini | 0 | n/a | 0 | collect more timing metadata before concurrency | low |

## Simulation
| stage | timing records | configured limit | sequential seconds | projected seconds | estimated saved seconds | reduction % | note |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| formatting | 6 | 2 | 84.91 | 84.91 | 0.00 | 0.0 | simulation withheld because stage has failed records |
| qa | 0 | 1 | 0.00 | 0.00 | 0.00 | 0.0 | configured limit is sequential |
| refining | 0 | 2 | 0.00 | 0.00 | 0.00 | 0.0 | insufficient completed timing records |
| translating | 0 | 2 | 0.00 | 0.00 | 0.00 | 0.0 | insufficient completed timing records |

## Safety Notes
- This report is not approval to set `execution.concurrency_enabled: true`.
- Glossary approval remains sequential and human-gated.
- QA and AI formatting must remain enabled in any benchmark.
- Stop on first hard failure, provider failure spike, command_too_long, or final-output guardrail regression.
