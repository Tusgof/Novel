# OpenRouter Bounded Block Probe - openrouter_bounded_block_probe_20260609_033555

## Summary

| Role | Route | Provider | Model | Score | Hard fail | Duration | Failure |
| --- | --- | --- | --- | ---: | --- | ---: | --- |
| glossary | openrouter_gemini3_flash | openrouter | `google/gemini-3-flash-preview` | 90 | True | 6.85s | none |
| glossary | current_gemini_pro | gemini | `pro` | 60 | True | 75.92s | quota |
| literal | openrouter_gemini3_flash | openrouter | `google/gemini-3-flash-preview` | 90 | True | 5.18s | none |
| literal | openrouter_deepseek_v4_flash | openrouter | `deepseek/deepseek-v4-flash` | 90 | True | 20.60s | none |
| literal | current_gemini_pro | gemini | `pro` | 45 | True | 29.92s | quota |
| refine | openrouter_gemini3_flash | openrouter | `google/gemini-3-flash-preview` | 100 | False | 5.30s | none |
| refine | openrouter_deepseek_v4_flash | openrouter | `deepseek/deepseek-v4-flash` | 100 | False | 19.39s | none |
| refine | openrouter_claude_sonnet_4_6 | openrouter | `anthropic/claude-sonnet-4.6` | 100 | False | 28.13s | none |
| qa | current_qwen_deepseek_reasoner | qwen | `deepseek-reasoner` | 90 | True | 39.27s | none |
| qa | openrouter_gemini3_flash | openrouter | `google/gemini-3-flash-preview` | 85 | True | 1.94s | none |
| qa | openrouter_deepseek_v4_pro | openrouter | `deepseek/deepseek-v4-pro` | 85 | True | 26.08s | none |
| format | openrouter_gemini3_flash | openrouter | `google/gemini-3-flash-preview` | 100 | False | 3.33s | none |
| format | openrouter_deepseek_v4_flash | openrouter | `deepseek/deepseek-v4-flash` | 100 | False | 13.27s | none |

## Recommendations

- `glossary`: first candidate `openrouter_gemini3_flash` (`google/gemini-3-flash-preview`), score 90, hard_fail=True.
- `literal`: first candidate `openrouter_gemini3_flash` (`google/gemini-3-flash-preview`), score 90, hard_fail=True.
- `refine`: first candidate `openrouter_gemini3_flash` (`google/gemini-3-flash-preview`), score 100, hard_fail=False.
- `qa`: first candidate `current_qwen_deepseek_reasoner` (`deepseek-reasoner`), score 90, hard_fail=True.
- `format`: first candidate `openrouter_gemini3_flash` (`google/gemini-3-flash-preview`), score 100, hard_fail=False.

Proposed next routing direction, pending Codex review:

```yaml
term_extraction: openrouter google/gemini-3-flash-preview
literal_translation: openrouter google/gemini-3-flash-preview
refinement: openrouter google/gemini-3-flash-preview
refinement fallback: openrouter deepseek/deepseek-v4-flash
qa_judge: keep current qwen/deepseek-reasoner unless OpenRouter QA wins the bounded probe
formatting: openrouter google/gemini-3-flash-preview with deterministic validation/local fallback
```

## Scope And Safety

- Non-production probe only.
- No production ledger, glossary notes, chapter work artifacts, final outputs, or provider routing config were modified by this probe.
- OpenRouter key was read by the shim from process/User environment and never written to artifacts.
- `.system/providers.yaml` changes are proposed only after this report; they are not applied by this script.
