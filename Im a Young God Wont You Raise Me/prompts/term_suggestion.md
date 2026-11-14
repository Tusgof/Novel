# Term Suggestion Prompt

Propose exactly 3 Thai options for the supplied term from I'm a Young God, Won't
You Raise Me? Use the supplied English relay/context and verified profile only.
Genre context is game-becomes-reality action/system fantasy.

## Category Guidance
- Keep the System role, Players, registered characters, UI commands and ordinary nouns distinct.
- Preserve the term's meaning and source register without importing other books' terminology.

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
