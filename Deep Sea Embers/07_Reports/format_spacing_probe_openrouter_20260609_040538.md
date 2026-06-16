# Format Spacing Probe - OpenRouter

Artifact dir: `D:\Fogust\Workspace\Novel\Deep Sea Embers\04_Work\_experiments\format_style_probe_20260609_040512`

| model | ok | score | seconds | issues | style checks |
| --- | --- | ---: | ---: | --- | --- |
| `deepseek/deepseek-v4-flash` | True | 100 | 23.64 | none | bold_bracket_panel=True, curly_dialogue=True, italic_thought=True, italic_sound=True, no_triple_blank=True, dialogue_standalone=True, panel_standalone=True, no_overescaped_markdown=True |
| `google/gemini-3-flash-preview` | True | 61 | 2.87 | none | bold_bracket_panel=True, curly_dialogue=True, italic_thought=False, italic_sound=False, no_triple_blank=True, dialogue_standalone=False, panel_standalone=True, no_overescaped_markdown=True |

Recommendation:

- Keep `deepseek/deepseek-v4-flash` as formatting primary if it stays above the fallback on spacing/style checks.
