# V6.36 Lean Pipeline Instrumentation

- Timestamp UTC: `2026-10-02`
- Status: implementation complete; glossary-projection smoke completed and stopped at QA
- Scope: traceability and experiment-only lean harness

## What Changed

1. Added opt-in provider tracing in `Deep Sea Embers/novel_pipeline/providers/trace.py`.
2. `ProviderRunner` now records one JSON trace per provider attempt when `NOVEL_PIPELINE_TRACE_DIR` is set.
3. OpenRouter shim writes provider-reported usage, model, request id, and finish reason to the trace collector.
4. Added `Deep Sea Embers/scripts/run_lean_pipeline_experiment.py`.
5. Added `Deep Sea Embers/prompts/term_harvest.md`.
6. Added a regression test for full prompt/response capture and secret redaction.
7. The lean literal stage now projects approved, chapter-relevant glossary terms into a source copy before the provider call. The original source remains the QA/refinement source of truth, and the literal prompt receives no glossary list.

## Lean Call Sequence

For each experiment chapter, the harness calls:

1. `literal_translation`: one provider call per transport-safe source block after longest-first replacement of chapter-relevant approved glossary terms in a projected source copy; no glossary list is attached to this prompt.
2. `refinement`: one provider call over the assembled literal chapter and the full source chapter.
3. `qa_judge`: one provider call comparing source, assembled literal, refined Thai, and relevant glossary.
4. `formatting`: one provider call over the refined chapter, followed by the existing deterministic fallback/validation path.
5. `term_harvest`: one provider call comparing source and final Thai. Valid candidates are written as `proposed`; production glossary files are not modified.

The existing production pipeline is unchanged by this implementation. The lean harness writes only to the caller-provided experiment output and trace directories.

## Trace Contents

Each `*.json` trace contains:

- run/chapter/stage/block context
- provider and model
- exact system prompt and user prompt
- prompt/output SHA-256 and character counts
- complete provider stdout/stderr
- return code, failure classification, timestamps, and duration
- provider-reported usage when available
- sanitized command metadata

API keys and bearer tokens are redacted. Full prompt/response files must remain local to an isolated experiment directory; research logs should reference paths and aggregate metrics rather than duplicating chapter text.

## Verification

- `python -m compileall novel_pipeline scripts\openrouter_provider_shim.py`: passed
- `PYTHONIOENCODING=utf-8 python test_translation.py`: passed
- `python scripts\run_lean_pipeline_experiment.py --help`: passed
- HGD `ch001` v2 smoke: stopped safely at refinement because DeepSeek returned an empty assistant message with `finish_reason=length` at the configured ceiling.
- HGD `ch001` v3 smoke: blocked before provider work because the command was started from the workspace root and the shared shim path resolved incorrectly.
- HGD `ch001` v4 smoke: literal and refinement calls completed with measured usage/cost (`12,737` tokens; `$0.01822778305`), then blocking QA stopped the run because refinement removed the approved `Nightmare Forge Studios` term. Trace inspection confirmed the literal prompt contained `none`, did not contain the original glossary term, and contained the projected Thai term. No final chapter output or MoonRead content was produced.

## Not Yet Measured

The implementation-only step made no provider call. The subsequent HGD smoke pilot made one real provider call, but it produced no translation output and measured no token usage or cost. No quality result, publication, or production replacement was performed.

## Next Safe Action

Classify and address the glossary-removal QA result in the isolated experiment before locking the cross-novel sample. Then run exact-route provider health checks, execute baseline before treatment, and stop if trace files are missing, redaction fails, provider access fails, or any production path is touched.
