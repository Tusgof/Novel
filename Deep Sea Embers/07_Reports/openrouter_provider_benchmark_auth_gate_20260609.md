# OpenRouter Provider Benchmark Auth Gate - 2026-06-09

## Verdict

Benchmark execution stopped at Phase A availability smoke because every OpenRouter model call returned:

```text
401 User not found
```

This is an authentication/account-key failure, not evidence that the candidate models are bad.

## Scope Attempted

Experiment directory:

```text
04_Work/_experiments/openrouter_provider_benchmark_20260609_024241
```

Generated smoke report:

```text
07_Reports/openrouter_provider_benchmark_20260609_024241.md
```

Models attempted:

- `deepseek/deepseek-v4-flash`
- `tencent/hy3-preview`
- `minimax/minimax-m3`
- `minimax/minimax-m3` repeatability rerun
- `xiaomi/mimo-v2.5`
- `openrouter/owl-alpha`
- `anthropic/claude-sonnet-4.6`
- `deepseek/deepseek-v4-pro`
- `deepseek/deepseek-v3.2`
- `google/gemini-3-flash-preview`

Calls attempted: 10 smoke calls.

## Result

All 10 calls reached OpenRouter and failed with HTTP 401:

```text
{"error":{"message":"User not found.","code":401}}
```

Observed key metadata:

- environment variable present: yes
- prefix shape: matches expected OpenRouter key prefix
- length: 73
- whitespace in value: no

The benchmark script did not print, store, or report the key value.

## Interpretation

The OpenRouter transport path works far enough to receive a structured OpenRouter error.

Likely causes:

- key is invalid, revoked, or not associated with an active OpenRouter user
- key belongs to a different environment/account than expected
- the environment variable contains a stale key, even though its shape is valid

Less likely:

- individual model failure, because all models failed identically before model execution
- prompt/output issue, because the API rejected authentication before generation

## Production Impact

No production route should be changed from this result.

The current production provider policy remains:

- Codex can continue covering literal/refinement where configured.
- Claude CLI remains unreliable due to session limits.
- Gemini remains a known slow/quota risk.
- Qwen formatting remains usable only under deterministic validation because prior formatting drift was observed.

## Files Created Or Changed

Created:

- `scripts/openrouter_provider_benchmark.py`
- `07_Reports/openrouter_provider_benchmark_20260609_024241.md`
- `07_Reports/openrouter_provider_benchmark_auth_gate_20260609.md`
- `04_Work/_experiments/openrouter_provider_benchmark_20260609_024241/`

Previously updated for V6.8 planning:

- `PROJECT_BRAIN.md`
- `IMPLEMENT_PLAN.md`
- `07_Reports/openrouter_provider_replacement_experiment_20260609.md`

Not modified by benchmark:

- `06_Logs/`
- `04_Work/ch*/`
- `05_Output/`
- `01_Glossary/`
- `.system/providers.yaml`
- production source files

## Next Required Action

Before running Phase B:

1. Confirm the OpenRouter key in the current shell is active in the OpenRouter dashboard.
2. Replace `OPENROUTER_API_KEY` in the shell environment only.
3. Rerun:

```powershell
python scripts/openrouter_provider_benchmark.py --smoke-only --timeout 90
```

Only after at least one model passes smoke should role-specific benchmark tasks run.
