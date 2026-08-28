# Immortality System Libra - Pilot Gate: Manual Glossary Stop

Date: 2026-08-28
Status: stopped by explicit manual-prompt policy
Scope: `immortality-libra-v1-insample`

## Stop Evidence

After the provider health check, the existing in-sample run resumed from its ledger and reached glossary approval for source term `林遠` in `ch1765`. The fallback route returned three safe Thai options, then the CLI requested a human selection. Because this bounded run was started with `--manual-action-mode stop`, the non-interactive process ended with EOF rather than selecting an option automatically.

Options shown by the pipeline:

1. `หลินหย่วน` - character name, close to the source pronunciation
2. `หลินเยวียน` - alternate pronunciation close to pinyin
3. `หลินหยวน` - shorter, readable Thai form

## Verified State

- Run status: `44` ledger records.
- Completed blocks: `ch1307-block-001` through `ch1307-block-004` only.
- Current failed blocks: none.
- `ch1765` has no new `glossary_approved` record and no translation output.
- The run produced no production output, production glossary mutation, or MoonRead content.
- The latest runtime Sentinel report for `ch1307` is `0/0/0/0`.

## Cause And Prevention

This stop is an expected manual-input boundary, not a provider failure: the provider fallback supplied usable candidates, but no human glossary decision was available to the bounded CLI process. Do not force-accept or invent a decision. After the user selects an option, approve that term through the existing glossary decision path, then resume the same run ID.
