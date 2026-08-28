# Immortality System Libra - Pilot Gate: Title Provider Stop

Date: 2026-08-28
Status: stopped before Pilot completion
Scope: isolated pilot title-sidecar preparation

## Verified State

- The Novel543 raw pool remains complete through `ch2570` (`2570/2570` usable chapters).
- The locked 20-chapter sample remains source-parity clean.
- The in-sample run remains stopped at glossary/translation preparation; no production output or MoonRead content exists.
- Valid title sidecars now exist for 11 of 20 sampled chapters: `ch1307`, `ch1765`, `ch2439`, `ch2307`, `ch741`, `ch1424`, `ch1631`, `ch376`, `ch338`, `ch984`, and `ch1410`.
- No pipeline process remained after the failed command, and the pilot ledger received no new records from title preparation.

## Stop Evidence

The bounded title batch `ch1020,ch2313,ch2358,ch1149,ch1653` failed during title refinement:

```text
Provider 'openrouter' returned unusable output (nonzero_exit).
OpenRouter shim error after 46.34s: OpenRouter returned an empty assistant message.
```

The command exited nonzero. It did not write title sidecars for the failed batch.

## Root Cause

The configured `refinement` route used `deepseek/deepseek-v4-flash`, which returned an empty assistant message for this request. `scripts/translate_chapter_titles.py` invokes the primary title provider directly and does not walk the configured refinement fallback chain, so the empty provider response stopped the whole bounded title batch.

## Prevention / Next Safe Action

- Treat the title preparation stop as a provider failure; do not resume the Pilot or start production from this state.
- Before the next resume, run a bounded provider health probe for the exact title-refinement prompt and verify the fallback behavior.
- Any code change to make title translation honor configured fallbacks must be reviewed and tested separately before rerunning the sample.
- Resume title preparation only for the missing sidecars, then resume `immortality-libra-v1-insample` from its existing ledger state.

## Scope Guard

- No production `05_Output` files were changed.
- No production glossary notes were changed.
- No MoonRead files were changed.
- No force-accept was used.

## Follow-up Verification

- The historical stop above remains a valid provider-failure record for the failed bounded batch.
- The canonical and isolated-experiment title helpers were updated to walk configured fallback routes and to record the route actually used in the sidecar metadata.
- Regression coverage passed in `Deep Sea Embers/test_translation.py` (`test_title_provider_uses_configured_fallback_after_primary_failure`).
- Current disk validation finds valid `title.json` sidecars for all 20 locked sample chapters.
- The Pilot remains blocked at glossary approval until the exact provider health checks pass; this follow-up does not authorize production translation or MoonRead publication.
