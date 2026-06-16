# OpenRouter Provider Benchmark Final Report - 2026-06-09

## Verdict

The OpenRouter experiment completed through smoke and role-specific benchmark tasks.

Best overall candidate:

- `google/gemini-3-flash-preview`

Recommended first production probe:

- Use `google/gemini-3-flash-preview` through an OpenRouter provider adapter for one bounded non-production block probe.

Do not switch production routing yet. The next step is to implement an OpenRouter provider adapter/shim and run one bounded block test before editing `.system/providers.yaml`.

## Execution Summary

Auth issue found first:

- Process environment key returned `401 User not found`.
- User environment key differed from process key and worked.
- Benchmark rerun used the User-scope `OPENROUTER_API_KEY` loaded into the shell for the command only.
- No key value was printed or written to disk.

Successful benchmark run:

```text
04_Work/_experiments/openrouter_provider_benchmark_20260609_025818
```

Generated report:

```text
07_Reports/openrouter_provider_benchmark_20260609_025818.md
```

Calls:

- 10 model slots
- 6 roles each
- 60 OpenRouter calls total

Roles:

- smoke
- glossary
- literal
- refine
- QA
- format

## Model Results

| Model | Calls | Hard fails | Avg score | Avg latency | Overall decision |
| --- | ---: | ---: | ---: | ---: | --- |
| `google/gemini-3-flash-preview` | 6 | 0 | 100.0 | 3.34s | primary candidate |
| `openrouter/owl-alpha` | 6 | 0 | 100.0 | 29.61s | fallback/research only; too slow and experimental |
| `deepseek/deepseek-v3.2` | 6 | 2 | 95.0 | 16.46s | candidate for refine/QA/format, not literal/glossary yet |
| `deepseek/deepseek-v4-flash` | 6 | 2 | 92.5 | 7.15s | candidate for literal/refine/format, not QA/glossary yet |
| `anthropic/claude-sonnet-4.6` | 6 | 2 | 95.0 | 26.71s | high-quality fallback, expensive/slow |
| `deepseek/deepseek-v4-pro` | 6 | 4 | 85.8 | 28.12s | QA/format only for now |
| `minimax/minimax-m3` | 12 | 8 | 83.3 | 19.91s | reject for structured production roles now |
| `xiaomi/mimo-v2.5` | 6 | 5 | 76.7 | 11.88s | reject for production routing now |
| `tencent/hy3-preview` | 6 | 6 | 75.0 | 20.68s | reject for production routing now |

## Role Recommendations

### Glossary / Term Extraction

1. `google/gemini-3-flash-preview`
   - score 100
   - latency 4.118s
   - best current candidate
2. `openrouter/owl-alpha`
   - score 100
   - latency 25.557s
   - usable but slow and experimental

Avoid for now:

- `deepseek/deepseek-v4-flash`
- `tencent/hy3-preview`
- `minimax/minimax-m3`
- `xiaomi/mimo-v2.5`
- `deepseek/deepseek-v4-pro`

Reason: malformed/truncated JSON or hard fail in structured glossary output.

### Literal Translation

1. `google/gemini-3-flash-preview`
   - score 100
   - latency 4.811s
   - best balanced candidate
2. `deepseek/deepseek-v4-flash`
   - score 100
   - latency 4.403s
   - cheap and fast; needs glossary-aware follow-up test before production
3. `openrouter/owl-alpha`
   - score 100
   - latency 45.198s
   - correct but too slow for main route

Watch item:

- The benchmark literal prompt did not fully enforce project glossary context. Before production routing, rerun a one-block probe with approved glossary terms and compare glossary usage.

### Refinement / Claude Replacement

1. `google/gemini-3-flash-preview`
   - score 100
   - latency 4.071s
   - strongest replacement candidate for Claude CLI refinement
2. `deepseek/deepseek-v4-flash`
   - score 100
   - latency 9.15s
   - good cheap candidate
3. `xiaomi/mimo-v2.5`
   - score 100
   - latency 15.025s
   - passed refine only, but failed other roles
4. `deepseek/deepseek-v3.2`
   - score 100
   - latency 24.153s
   - good quality, slower
5. `anthropic/claude-sonnet-4.6`
   - score 100
   - latency 92.815s
   - quality route but too slow/costly as primary

Recommended route hypothesis:

- primary: `google/gemini-3-flash-preview`
- fallback: `deepseek/deepseek-v4-flash`
- high-quality fallback only: `anthropic/claude-sonnet-4.6`

### QA

Passed known-bad perspective-drift fixture:

- `google/gemini-3-flash-preview`
- `openrouter/owl-alpha`
- `deepseek/deepseek-v3.2`
- `anthropic/claude-sonnet-4.6`
- `deepseek/deepseek-v4-pro`

Failed known-bad QA fixture:

- `deepseek/deepseek-v4-flash`
- `xiaomi/mimo-v2.5`
- `minimax/minimax-m3`
- `tencent/hy3-preview`

Recommended QA route hypothesis:

- primary: keep current Qwen route until a bounded probe proves replacement
- OpenRouter candidate: `google/gemini-3-flash-preview`
- fallback candidate: `deepseek/deepseek-v3.2`

### Formatting

Passed deterministic content-preservation check:

- `google/gemini-3-flash-preview`
- `deepseek/deepseek-v4-flash`
- `deepseek/deepseek-v3.2`
- `anthropic/claude-sonnet-4.6`
- `minimax/minimax-m3`
- `openrouter/owl-alpha`
- `deepseek/deepseek-v4-pro`

Failed/truncated:

- `xiaomi/mimo-v2.5`
- `tencent/hy3-preview`

Recommended formatting route hypothesis:

- primary: `google/gemini-3-flash-preview`
- cheap fallback: `deepseek/deepseek-v4-flash`
- always keep deterministic validation and local fallback

## Production Routing Proposal

Do not edit `.system/providers.yaml` yet.

Recommended next implementation:

1. Add an OpenRouter provider adapter/shim that:
   - reads `OPENROUTER_API_KEY` from process/User env
   - calls `https://openrouter.ai/api/v1/chat/completions`
   - passes prompt through stdin or temp file safely
   - never logs bearer tokens
   - returns stdout compatible with existing `ProviderRunner`
2. Run one bounded non-production block probe:
   - glossary: `google/gemini-3-flash-preview`
   - literal: `google/gemini-3-flash-preview` versus `deepseek/deepseek-v4-flash`
   - refine: `google/gemini-3-flash-preview` versus `deepseek/deepseek-v4-flash`
   - QA: current Qwen versus `google/gemini-3-flash-preview`
   - format: `google/gemini-3-flash-preview` versus `deepseek/deepseek-v4-flash`
3. Only after the bounded block probe passes, propose `.system/providers.yaml` changes.

First proposed production candidate after bounded probe:

```yaml
term_extraction: google/gemini-3-flash-preview via OpenRouter
literal_translation: google/gemini-3-flash-preview via OpenRouter
refinement: google/gemini-3-flash-preview via OpenRouter
qa_judge: keep qwen/deepseek-reasoner initially; test google/gemini-3-flash-preview as fallback
formatting: google/gemini-3-flash-preview via OpenRouter with deterministic validation/local fallback
```

Cheap fallback candidates:

```yaml
literal_translation fallback: deepseek/deepseek-v4-flash
refinement fallback: deepseek/deepseek-v4-flash
formatting fallback: deepseek/deepseek-v4-flash
qa fallback: deepseek/deepseek-v3.2
```

## Security And Integrity Checks

- API key was loaded from environment only.
- API key value was not printed.
- API key value was not written to files.
- No production ledger files were modified by the benchmark.
- No `04_Work/ch*/` artifacts were intentionally modified by the benchmark.
- No final outputs were modified by the benchmark.
- No glossary notes were modified by the benchmark.
- `.system/providers.yaml` was not changed by the benchmark.

## Limitations

- Benchmark prompts are role fixtures, not full production prompts.
- Literal task needs a stricter glossary-aware follow-up before production routing.
- Scores are deterministic-harness scores, not a substitute for one bounded block probe.
- `openrouter/owl-alpha` is free and passed all tasks, but it is too slow and experimental for primary production routing.
- `anthropic/claude-sonnet-4.6` avoids local Claude session limits but is slow and comparatively expensive.

## Final Recommendation

Proceed with V6.8D:

- implement OpenRouter provider adapter/shim
- run a bounded block probe using `google/gemini-3-flash-preview` as the main candidate
- keep `deepseek/deepseek-v4-flash` as cheap candidate for literal/refine/format
- keep `deepseek/deepseek-v3.2` as QA fallback candidate
- do not use `tencent/hy3-preview`, `xiaomi/mimo-v2.5`, or `minimax/minimax-m3` for production routing yet
