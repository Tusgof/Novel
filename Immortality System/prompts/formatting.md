# Formatting Prompt

Format the supplied Thai novel prose as clean Markdown without changing its words,
meaning, order, or punctuation semantics.

Rules:
- Preserve every sentence and every content-bearing mark.
- Keep a direct speech line as its own paragraph when it is clearly separable.
- Keep a clear inner thought or standalone sound effect as its own paragraph and use
  italics only when the source text makes that function clear.
- Use bold bracket formatting for clear system/status/skill/notification panels that
  are already represented as labels or bracketed text.
- Keep one blank line between narrative paragraphs, dialogue, thoughts, sound effects,
  and system panels. Remove excessive blank lines.
- Do not translate, rewrite, summarize, add, or remove content.
- Do not invent headings, dividers, speaker names, or decorative lines.
- Return formatted Markdown only.

Text to format:
{{text}}
