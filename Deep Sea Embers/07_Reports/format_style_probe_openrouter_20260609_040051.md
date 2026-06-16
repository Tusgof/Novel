# Format Style Probe - OpenRouter

Artifact dir: `D:\Fogust\Workspace\Novel\Deep Sea Embers\04_Work\_experiments\format_style_probe_20260609_040020`

| model | ok | score | seconds | issues | style checks |
| --- | --- | ---: | ---: | --- | --- |
| `google/gemini-3-flash-preview` | True | 74 | 3.27 | none | bold_bracket_panel=True, curly_dialogue=True, italic_thought=False, italic_sound=False, separator_or_grouping=True, no_overescaped_markdown=True |
| `deepseek/deepseek-v4-flash` | True | 100 | 28.11 | none | bold_bracket_panel=True, curly_dialogue=True, italic_thought=True, italic_sound=True, separator_or_grouping=True, no_overescaped_markdown=True |

Recommendation:

- Use `deepseek/deepseek-v4-flash` as formatting primary for now; keep the other tested model as fallback.
