# Immortality System Libra - Pilot Gate: Resume Stop

Date: 2026-08-28
Status: stopped before Pilot completion
Scope: `immortality-libra-v1-insample`

## Verified State

- Novel543 raw source is complete through `ch2570` (`2570/2570` usable chapters).
- The locked 20-chapter sample still has source parity `0` mismatches.
- In-sample scan has `73` candidates; out-of-sample scan has `66` candidates.
- The experiment glossary now has `47/47` parseable approved notes after repairing stale frontmatter.
- `ch1307` completed all four blocks, final assembly, and runtime Sentinel with blocker/major/minor/info `0/0/0/0`.
- `ch1307` is experiment output only. No production output, production glossary, or MoonRead content was changed.

## Stop Evidence

The resumed in-sample run stopped while approving the term `林遠` for `ch1765`.
The configured provider chain did not produce three safe Thai options. The final fallback
failed with an expired Claude OAuth session:

```text
No safe Thai glossary options for '林遠' after configured provider fallbacks.
Provider 'claude' returned unusable output (nonzero_exit).
Failed to authenticate: OAuth session expired and could not be refreshed
```

The run exited nonzero. No force-accept was used, and `ch1765` glossary approval was not
committed. This is a provider-chain stop, not a content approval.

## Root Causes

1. The normal DeepSeek V4 Flash term-suggestion request can return an empty assistant message;
   this was reproduced by the bounded health probe.
2. The fallback chain reached a Claude provider whose local OAuth session had expired. The
   chain therefore had no usable route for `林遠`.
3. Title sidecars were not prepared for the full pilot sample before translation. The existing
   final-assembly guard correctly stopped `ch1307` until its `title.json` was generated.
4. A stale experiment glossary template had previously produced notes without an opening YAML
   delimiter and with duplicated `source_language`; those notes were repaired and now parse.

## Prevention

- Keep glossary suggestion fail-closed: if all configured routes fail or return fewer than three
  safe Thai options, raise a provider output failure instead of generating source-language
  fallback options.
- Before resuming a pilot or production range, run the exact provider health probe and verify
  that the configured fallback credentials are usable. Do not treat a fallback authentication
  error as a successful translation.
- Prepare and validate title sidecars for every sampled chapter before block translation, while
  retaining final assembly as a blocking backstop.
- Validate every newly written glossary note with the same parser before committing the chapter's
  `glossary_approved` stage.

## Next Safe Action

Do not resume this run until the provider chain is healthy or an explicitly approved routing
change is made. After that, resume the existing run ID from `ch1765`, generate/validate the
remaining sample title sidecars, complete in-sample and out-of-sample Pilot measurement, and
only then consider production `ch001-ch060`.

## Artifacts

- `04_Work/_experiments/libra_pilot_immortality_system_v1/06_Logs/run_ledger.jsonl`
- `04_Work/_experiments/libra_pilot_immortality_system_v1/07_Reports/provider_usage_immortality-libra-v1-insample.md`
- `04_Work/_experiments/libra_pilot_immortality_system_v1/04_Work/ch1307/title.json`
- `04_Work/_experiments/libra_pilot_immortality_system_v1/05_Output/ch1307/ch1307.md`
- `07_Reports/immortality_system_libra_pilot_provider_stop_20260828.md`
