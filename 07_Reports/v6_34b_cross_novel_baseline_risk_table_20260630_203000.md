# V6.34B Cross-Novel Baseline Risk Table

- Timestamp UTC: `2026-06-30T20:30:16Z`
- Provider calls: `0`
- Source: fetched `03_Raw/` only
- Sample seed: `634001`

## Summary

| Novel | Rows | Missing source | Glossary terms loaded | Top flags |
| --- | ---: | ---: | ---: | --- |
| deep-sea-embers | 20 | 0 | 168 | title_sidecar_required=20, footnote_or_author_note_risk=18, high_glossary_density=16, very_high_glossary_density=4 |
| horror-game-developer | 20 | 0 | 297 | high_glossary_density=14, bracket_system_density=2, long_source=1 |
| infinite-regressor-stories | 20 | 0 | 363 | footnote_or_author_note_risk=17, high_glossary_density=11, long_source=11, very_long_source=9, very_high_glossary_density=7 |

## Highest-Risk Chapters

| Novel | Split | Chapter | Chars | Glossary hits | Flags |
| --- | --- | --- | ---: | ---: | --- |
| infinite-regressor-stories | out_of_sample | ch133 | 12485 | 20 | long_source, bracket_system_density, repeated_character_risk, footnote_or_author_note_risk, very_high_glossary_density, embedded_cjk_source_risk |
| infinite-regressor-stories | out_of_sample | ch093 | 14954 | 10 | very_long_source, footnote_or_author_note_risk, high_glossary_density, hangul_name_source_risk, embedded_cjk_source_risk |
| infinite-regressor-stories | in_sample | ch086 | 14831 | 12 | very_long_source, bracket_system_density, footnote_or_author_note_risk, high_glossary_density, embedded_cjk_source_risk |
| infinite-regressor-stories | in_sample | ch009 | 14510 | 32 | very_long_source, high_bracket_system_density, footnote_or_author_note_risk, very_high_glossary_density, embedded_cjk_source_risk |
| infinite-regressor-stories | out_of_sample | ch278 | 11678 | 26 | long_source, high_bracket_system_density, repeated_character_risk, footnote_or_author_note_risk, very_high_glossary_density |
| infinite-regressor-stories | in_sample | ch201 | 14204 | 26 | very_long_source, repeated_character_risk, footnote_or_author_note_risk, very_high_glossary_density |
| infinite-regressor-stories | in_sample | ch076 | 14018 | 11 | very_long_source, repeated_character_risk, footnote_or_author_note_risk, high_glossary_density |
| infinite-regressor-stories | in_sample | ch300 | 13972 | 32 | long_source, bracket_system_density, footnote_or_author_note_risk, very_high_glossary_density |
| infinite-regressor-stories | out_of_sample | ch073 | 13948 | 21 | long_source, repeated_character_risk, footnote_or_author_note_risk, very_high_glossary_density |
| infinite-regressor-stories | out_of_sample | ch030 | 13409 | 19 | long_source, bracket_system_density, footnote_or_author_note_risk, high_glossary_density |
| infinite-regressor-stories | out_of_sample | ch236 | 12431 | 22 | long_source, high_bracket_system_density, footnote_or_author_note_risk, very_high_glossary_density |
| infinite-regressor-stories | in_sample | ch157 | 10815 | 11 | long_source, high_bracket_system_density, footnote_or_author_note_risk, high_glossary_density |
| infinite-regressor-stories | out_of_sample | ch165 | 9732 | 14 | long_source, high_bracket_system_density, footnote_or_author_note_risk, high_glossary_density |
| infinite-regressor-stories | in_sample | ch338 | 17923 | 13 | very_long_source, footnote_or_author_note_risk, high_glossary_density |
| infinite-regressor-stories | in_sample | ch252 | 15210 | 16 | very_long_source, bracket_system_density, high_glossary_density |
| infinite-regressor-stories | in_sample | ch183 | 14181 | 6 | very_long_source, repeated_character_risk, footnote_or_author_note_risk |
| infinite-regressor-stories | out_of_sample | ch244 | 13101 | 11 | long_source, footnote_or_author_note_risk, high_glossary_density |
| infinite-regressor-stories | in_sample | ch381 | 10704 | 5 | long_source, high_bracket_system_density, footnote_or_author_note_risk |
| deep-sea-embers | in_sample | ch150 | 3038 | 23 | footnote_or_author_note_risk, very_high_glossary_density, title_sidecar_required |
| deep-sea-embers | out_of_sample | ch132 | 2945 | 9 | footnote_or_author_note_risk, high_glossary_density, title_sidecar_required |

## Per-Chapter Table

| Novel | Split | Chapter | Chars | Brackets | Repeats | Footnotes | Glossary hits | Flags |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| deep-sea-embers | in_sample | ch008 | 2840 | 0 | 0 | 4 | 9 | footnote_or_author_note_risk, high_glossary_density, title_sidecar_required |
| deep-sea-embers | in_sample | ch033 | 2759 | 0 | 0 | 4 | 18 | footnote_or_author_note_risk, high_glossary_density, title_sidecar_required |
| deep-sea-embers | in_sample | ch051 | 2879 | 0 | 0 | 0 | 21 | very_high_glossary_density, title_sidecar_required |
| deep-sea-embers | in_sample | ch061 | 2807 | 0 | 0 | 2 | 11 | footnote_or_author_note_risk, high_glossary_density, title_sidecar_required |
| deep-sea-embers | in_sample | ch077 | 2827 | 0 | 0 | 4 | 13 | footnote_or_author_note_risk, high_glossary_density, title_sidecar_required |
| deep-sea-embers | in_sample | ch098 | 2942 | 0 | 0 | 6 | 16 | footnote_or_author_note_risk, high_glossary_density, title_sidecar_required |
| deep-sea-embers | in_sample | ch110 | 2867 | 0 | 0 | 2 | 22 | footnote_or_author_note_risk, very_high_glossary_density, title_sidecar_required |
| deep-sea-embers | in_sample | ch143 | 2853 | 0 | 0 | 4 | 17 | footnote_or_author_note_risk, high_glossary_density, title_sidecar_required |
| deep-sea-embers | in_sample | ch150 | 3038 | 0 | 0 | 2 | 23 | footnote_or_author_note_risk, very_high_glossary_density, title_sidecar_required |
| deep-sea-embers | in_sample | ch176 | 2886 | 0 | 0 | 1 | 20 | footnote_or_author_note_risk, very_high_glossary_density, title_sidecar_required |
| deep-sea-embers | out_of_sample | ch016 | 2812 | 0 | 0 | 1 | 17 | footnote_or_author_note_risk, high_glossary_density, title_sidecar_required |
| deep-sea-embers | out_of_sample | ch027 | 2782 | 0 | 0 | 1 | 13 | footnote_or_author_note_risk, high_glossary_density, title_sidecar_required |
| deep-sea-embers | out_of_sample | ch044 | 2823 | 0 | 0 | 1 | 19 | footnote_or_author_note_risk, high_glossary_density, title_sidecar_required |
| deep-sea-embers | out_of_sample | ch072 | 2878 | 0 | 0 | 4 | 18 | footnote_or_author_note_risk, high_glossary_density, title_sidecar_required |
| deep-sea-embers | out_of_sample | ch089 | 2849 | 0 | 0 | 3 | 10 | footnote_or_author_note_risk, high_glossary_density, title_sidecar_required |
| deep-sea-embers | out_of_sample | ch099 | 2841 | 0 | 0 | 3 | 18 | footnote_or_author_note_risk, high_glossary_density, title_sidecar_required |
| deep-sea-embers | out_of_sample | ch125 | 2916 | 0 | 0 | 5 | 14 | footnote_or_author_note_risk, high_glossary_density, title_sidecar_required |
| deep-sea-embers | out_of_sample | ch132 | 2945 | 0 | 0 | 4 | 9 | footnote_or_author_note_risk, high_glossary_density, title_sidecar_required |
| deep-sea-embers | out_of_sample | ch154 | 2897 | 0 | 0 | 1 | 13 | footnote_or_author_note_risk, high_glossary_density, title_sidecar_required |
| deep-sea-embers | out_of_sample | ch180 | 2866 | 0 | 0 | 0 | 16 | high_glossary_density, title_sidecar_required |
| horror-game-developer | in_sample | ch005 | 6986 | 0 | 0 | 0 | 11 | high_glossary_density |
| horror-game-developer | in_sample | ch046 | 6963 | 0 | 0 | 0 | 8 | high_glossary_density |
| horror-game-developer | in_sample | ch059 | 6109 | 2 | 0 | 0 | 4 | none |
| horror-game-developer | in_sample | ch083 | 7867 | 0 | 0 | 0 | 14 | high_glossary_density |
| horror-game-developer | in_sample | ch131 | 8112 | 0 | 0 | 0 | 9 | high_glossary_density |
| horror-game-developer | in_sample | ch155 | 8112 | 1 | 0 | 0 | 7 | none |
| horror-game-developer | in_sample | ch187 | 7126 | 2 | 0 | 0 | 14 | high_glossary_density |
| horror-game-developer | in_sample | ch205 | 6928 | 3 | 0 | 0 | 17 | high_glossary_density |
| horror-game-developer | in_sample | ch239 | 7133 | 8 | 0 | 0 | 10 | bracket_system_density, high_glossary_density |
| horror-game-developer | in_sample | ch262 | 8388 | 0 | 0 | 0 | 2 | none |
| horror-game-developer | out_of_sample | ch027 | 8430 | 2 | 0 | 0 | 12 | high_glossary_density |
| horror-game-developer | out_of_sample | ch041 | 7158 | 0 | 0 | 0 | 12 | high_glossary_density |
| horror-game-developer | out_of_sample | ch067 | 6490 | 3 | 0 | 0 | 5 | none |
| horror-game-developer | out_of_sample | ch097 | 8074 | 3 | 0 | 0 | 14 | high_glossary_density |
| horror-game-developer | out_of_sample | ch124 | 7830 | 0 | 0 | 0 | 14 | high_glossary_density |
| horror-game-developer | out_of_sample | ch160 | 6958 | 2 | 0 | 0 | 4 | none |
| horror-game-developer | out_of_sample | ch186 | 9709 | 0 | 0 | 0 | 12 | long_source, high_glossary_density |
| horror-game-developer | out_of_sample | ch204 | 7321 | 0 | 0 | 0 | 9 | high_glossary_density |
| horror-game-developer | out_of_sample | ch242 | 7516 | 0 | 0 | 0 | 7 | none |
| horror-game-developer | out_of_sample | ch252 | 6803 | 7 | 0 | 0 | 11 | bracket_system_density, high_glossary_density |
| infinite-regressor-stories | in_sample | ch009 | 14510 | 21 | 2 | 1 | 32 | very_long_source, high_bracket_system_density, footnote_or_author_note_risk, very_high_glossary_density, embedded_cjk_source_risk |
| infinite-regressor-stories | in_sample | ch076 | 14018 | 2 | 6 | 1 | 11 | very_long_source, repeated_character_risk, footnote_or_author_note_risk, high_glossary_density |
| infinite-regressor-stories | in_sample | ch086 | 14831 | 4 | 1 | 1 | 12 | very_long_source, bracket_system_density, footnote_or_author_note_risk, high_glossary_density, embedded_cjk_source_risk |
| infinite-regressor-stories | in_sample | ch157 | 10815 | 46 | 1 | 1 | 11 | long_source, high_bracket_system_density, footnote_or_author_note_risk, high_glossary_density |
| infinite-regressor-stories | in_sample | ch183 | 14181 | 0 | 12 | 1 | 6 | very_long_source, repeated_character_risk, footnote_or_author_note_risk |
| infinite-regressor-stories | in_sample | ch201 | 14204 | 0 | 8 | 1 | 26 | very_long_source, repeated_character_risk, footnote_or_author_note_risk, very_high_glossary_density |
| infinite-regressor-stories | in_sample | ch252 | 15210 | 7 | 2 | 0 | 16 | very_long_source, bracket_system_density, high_glossary_density |
| infinite-regressor-stories | in_sample | ch300 | 13972 | 4 | 1 | 1 | 32 | long_source, bracket_system_density, footnote_or_author_note_risk, very_high_glossary_density |
| infinite-regressor-stories | in_sample | ch338 | 17923 | 2 | 1 | 1 | 13 | very_long_source, footnote_or_author_note_risk, high_glossary_density |
| infinite-regressor-stories | in_sample | ch381 | 10704 | 60 | 1 | 1 | 5 | long_source, high_bracket_system_density, footnote_or_author_note_risk |
| infinite-regressor-stories | out_of_sample | ch030 | 13409 | 6 | 2 | 1 | 19 | long_source, bracket_system_density, footnote_or_author_note_risk, high_glossary_density |
| infinite-regressor-stories | out_of_sample | ch073 | 13948 | 3 | 5 | 1 | 21 | long_source, repeated_character_risk, footnote_or_author_note_risk, very_high_glossary_density |
| infinite-regressor-stories | out_of_sample | ch093 | 14954 | 1 | 1 | 1 | 10 | very_long_source, footnote_or_author_note_risk, high_glossary_density, hangul_name_source_risk, embedded_cjk_source_risk |
| infinite-regressor-stories | out_of_sample | ch133 | 12485 | 5 | 9 | 1 | 20 | long_source, bracket_system_density, repeated_character_risk, footnote_or_author_note_risk, very_high_glossary_density, embedded_cjk_source_risk |
| infinite-regressor-stories | out_of_sample | ch165 | 9732 | 19 | 1 | 1 | 14 | long_source, high_bracket_system_density, footnote_or_author_note_risk, high_glossary_density |
| infinite-regressor-stories | out_of_sample | ch236 | 12431 | 21 | 2 | 1 | 22 | long_source, high_bracket_system_density, footnote_or_author_note_risk, very_high_glossary_density |
| infinite-regressor-stories | out_of_sample | ch244 | 13101 | 3 | 2 | 1 | 11 | long_source, footnote_or_author_note_risk, high_glossary_density |
| infinite-regressor-stories | out_of_sample | ch278 | 11678 | 12 | 8 | 1 | 26 | long_source, high_bracket_system_density, repeated_character_risk, footnote_or_author_note_risk, very_high_glossary_density |
| infinite-regressor-stories | out_of_sample | ch348 | 14146 | 0 | 1 | 0 | 18 | very_long_source, high_glossary_density |
| infinite-regressor-stories | out_of_sample | ch361 | 9036 | 2 | 1 | 0 | 9 | long_source, high_glossary_density |
