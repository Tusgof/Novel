# TDU Provider Route Recovery

## Scope

- Novel: Ten Day Ultimatum
- Authorized continuation: `TDU-LEAN-PROD-20261007-ch011-020`
- This change is configuration and transport recovery only. It does not resume translation, promote output, or publish MoonRead content.

## Root Cause

- **Measured:** The latest bounded run stopped during literal translation after OpenRouter returned HTTP `429` with `Retry-After: 10`.
- **Measured:** The OpenRouter shim ignored the provider delay and used only its configured retry delay.
- **Measured:** The next configured route was Codex `gpt-5.4`, which failed with HTTP `503` because no account supported that model.
- **Inferred:** Retrying the same route without honoring `Retry-After`, or keeping the dead Codex route, would reproduce the incident without improving the run.

## Changes

1. All workspace OpenRouter shims now parse numeric `Retry-After` and sleep for the larger of the configured delay and the provider delay.
2. Added a regression test proving a `429` with `Retry-After: 10` waits 10 seconds before retrying.
3. TDU now uses the authenticated direct Claude CLI route (`claude/sonnet`) instead of the unsupported `codex/gpt-5.4` fallback for term extraction, literal translation, and refinement. TDU setup/fetch also use Claude as their primary route.
4. Added routing regression coverage preventing the known unsupported Codex fallback from returning to TDU.

## Verification

- **Measured:** `python test_translation.py` from `Deep Sea Embers`: passed, including the OpenRouter shim regression.
- **Measured:** `python -m unittest -v test_workspace_routing.py test_xszj_adapter.py`: `23/23` passed.
- **Measured:** `python -m compileall -q novel_pipeline scripts` plus selected novel provider helpers: passed.
- **Measured:** `git diff --check`: passed.
- **Measured:** `claude auth status`: logged in through `claude.ai` with a Pro subscription; credential values were not read or recorded.
- **Measured:** TDU preflight detects the Claude executable and routes it for the affected stages.
- **Not yet measured:** A real Claude generation call. Provider-backed route health and translation quality must be proven by the next bounded resume.

## Safe Next Action

After this change is landed with green CI, issue a fresh bounded resume for exactly `ch011-ch020`. Reuse only matching checkpoints, require the full final guardrail/Sentinel/spot-check gate, and keep MoonRead unchanged until all ten chapters pass. If Claude or OpenRouter fails again, preserve evidence and stop at the provider rule.

