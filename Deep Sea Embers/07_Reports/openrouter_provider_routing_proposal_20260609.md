# OpenRouter Provider Routing Proposal - 2026-06-09

## Status

Proposal only. This file does not apply routing changes.

Evidence:

- benchmark report: `07_Reports/openrouter_provider_benchmark_final_20260609.md`
- bounded block probe: `07_Reports/openrouter_bounded_block_probe_final_20260609.md`
- probe artifacts: `04_Work/_experiments/openrouter_bounded_block_probe_20260609_033555/`

## Probe Result Summary

OpenRouter `google/gemini-3-flash-preview` passed all bounded probe roles:

- glossary: 100, no hard fail, 6.85s
- literal: 100, no hard fail, 5.18s
- refine: 100, no hard fail, 5.30s
- QA: 100, no hard fail, 1.94s
- format: 100, no hard fail, 3.33s

Current Gemini CLI `pro` failed quota in both tested roles:

- glossary: quota failure, 75.92s
- literal: quota failure, 29.92s

Other useful candidates:

- `deepseek/deepseek-v4-flash`
  - literal: 100, no hard fail, 20.60s
  - refine: 100, no hard fail, 19.39s
  - format: 100, no hard fail, 13.27s
- `anthropic/claude-sonnet-4.6`
  - refine: 100, no hard fail, 28.13s
- `deepseek/deepseek-v4-pro`
  - QA: 100, no hard fail, 26.08s
- current `qwen/deepseek-reasoner`
  - QA: 100, no hard fail, 39.27s

## Recommended Routing Direction

Use OpenRouter Gemini 3 Flash Preview as the first replacement for Gemini CLI and local Claude CLI bottlenecks.

Recommended staged route:

```yaml
term_extraction:
  provider: openrouter
  model: google/gemini-3-flash-preview

literal_translation:
  provider: openrouter
  model: google/gemini-3-flash-preview

refinement:
  provider: openrouter
  model: google/gemini-3-flash-preview
  fallbacks:
    - provider: openrouter
      model: deepseek/deepseek-v4-flash
    - provider: openrouter
      model: anthropic/claude-sonnet-4.6
    - provider: codex
      model: gpt-5.4

qa_judge:
  provider: openrouter
  model: google/gemini-3-flash-preview
  fallbacks:
    - provider: qwen
      model: deepseek-reasoner
    - provider: openrouter
      model: deepseek/deepseek-v4-pro

formatting:
  provider: openrouter
  model: google/gemini-3-flash-preview
  fallbacks:
    - provider: openrouter
      model: deepseek/deepseek-v4-flash
```

## Provider Spec Fragment

Candidate provider spec for `.system/providers.yaml`:

```yaml
providers:
  openrouter:
    executable:
      - C:\Users\ASUS\AppData\Local\Programs\Python\Python314\python.exe
      - scripts\openrouter_provider_shim.py
    prompt_flag:
    prompt_position: positional
    prompt_transport: stdin
    model_flag: -m
    model_position: before_prompt
    default_model: google/gemini-3-flash-preview
    timeout_seconds: 360
    retry:
      max_attempts: 1
      initial_delay_seconds: 0
      backoff_multiplier: 1.0
      failure_kinds:
        - quota
        - timeout
        - nonzero_exit
        - empty_stdout
```

## Why Not Apply Automatically

Do not apply this directly until Codex/user approves because:

- `.system/providers.yaml` is already dirty from prior production workaround routing.
- active translation run `deep-sea-embers-retranslate-ch024-ch028-v1` is paused mid-batch.
- changing routes mid-run is acceptable only when intentionally done and documented.
- production should run one short recovery/resume slice after config change and validate output before larger continuation.

## Proposed Next Safe Action

1. Review this proposal.
2. If accepted, patch `.system/providers.yaml` with an `openrouter` provider and staged routes.
3. Run deterministic validation:

```powershell
python -m compileall novel_pipeline
python test_translation.py
novel-pipeline --config ".system/config.yaml" preflight
```

4. Continue the active run only to the current chapter boundary first:

```powershell
novel-pipeline --config ".system/config.yaml" resume --run-id deep-sea-embers-retranslate-ch024-ch028-v1 --manual-action-mode stop --until-chapter ch028
```

5. Validate ch024-ch028 outputs before starting ch029+.
