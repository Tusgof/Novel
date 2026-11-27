# DSE Lean ch021-ch030 recovery checkpoint

- Run: `DSE-LEAN-PROD-20261008-ch026-030-v1`
- Scope: `ch026-ch030` (continuation of the verified `ch021-ch025` run)
- Status: **blocked by provider exhaustion**; no MoonRead publication was run.

## Measured state

- `ch027`: promoted by the Lean runner; Sentinel `0/0/0/0`.
- `ch028`: promoted by the Lean runner; Sentinel `0/0/0/0` after deterministic whitespace reflow.
- `ch029`: QA passed and the staged Markdown exists; stage-only Sentinel `0/0/0/0`. Promotion is pending the normal term-harvest stage, which exhausted its configured routes.
- `ch026`: remains quarantined. The latest refined checkpoint now has no rule-based QA findings after restoring the approved `身体 -> ร่างกาย` term, but provider QA has not rerun.
- `ch030`: has literal and refinement checkpoints only; QA and promotion have not run.
- Existing output guardrails for `ch021-ch030` passed. This checks the current `05_Output` surface; it does not make quarantined chapters publishable.

## Repairs recorded

- `ch026/literal_checkpoint.json`: restored the rhetorical question and the repeated `像话吗` line from the source-backed QA findings.
- `ch026/refined_checkpoint.json`: restored the approved glossary term at the corresponding passage; rule QA is now clean.
- `ch028/formatted_checkpoint.json`: split dense paragraphs at existing whitespace boundaries; max paragraph length changed from `1574` to `830` and content-signature validation passed.
- `ch029/refined_checkpoint.json`: restored the named book title as `ก้าวเข้าสู่ความไม่เป็นวิทยาศาสตร์`; the subsequent QA checkpoint passed.

## Blocking evidence

The final resume stopped at the configured term-harvest route after OpenRouter returned HTTP 402 for the 12,000-token cap, the fallback OpenRouter route timed out, and the Codex fallback returned HTTP 503 because no account supports `gpt-5.4`. Do not change routing or bypass QA/term-harvest checkpoints; resume the same run after provider capacity is restored.

## Next safe action

Resume the exact run and range with the existing config and `--resume`. Confirm `ch026`, `ch029`, and `ch030` pass QA, formatting, guardrails, and Sentinel before updating the registry or running MoonRead `publish:verify` for `ch021-ch030`.
