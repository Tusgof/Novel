# Format Style Probe - OpenRouter

Artifact dir: `D:\Fogust\Workspace\Novel\Deep Sea Embers\04_Work\_experiments\format_style_probe_20260609_035913`

| model | ok | score | seconds | issues | style checks |
| --- | --- | ---: | ---: | --- | --- |
| `google/gemini-3-flash-preview` | False | 0 | 3.54 | Provider 'openrouter' returned unusable output (empty_stdout).  |  |
| `deepseek/deepseek-v4-flash` | False | 0 | 15.84 | Provider 'openrouter' returned unusable output (empty_stdout).  |  |

Recommendation:

- Use `google/gemini-3-flash-preview` as formatting primary for now; keep the other tested model as fallback.
