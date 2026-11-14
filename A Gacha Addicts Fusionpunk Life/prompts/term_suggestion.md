# Term Suggestion Prompt

Propose exactly 3 natural Thai translation options for the supplied source term
from A Gacha Addict's Fusionpunk Life. Use only the supplied source/context and
verified novel profile. Do not inherit names, lore or register from another book.

## Category Guidance
- Preserve verified proper-name identity and distinguish technology, magic and game-system terms.
- Use relationships and scene context for honorifics/register; do not invent a Korean original or extra lore.

## Source Term
- Original: {{original_term}}
- Category: {{category}}
- Source Language: {{source_language}}

## Context from Novel
{{context}}

## Output Rules
- Return exactly 3 options, one per line.
- Each line MUST follow the format: `Thai Term | Brief Rationale`
- The `Thai Term` must be concise (1-5 words).
- The `Brief Rationale` should explain why this option is suitable for the context/tone.
- Do NOT include any numbering, bullets, or markdown.
- Do NOT include any extra text.

## Output Format
Thai Term 1 | Rationale 1
Thai Term 2 | Rationale 2
Thai Term 3 | Rationale 3
