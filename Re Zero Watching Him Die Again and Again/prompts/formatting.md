# Re:Zero Thai Formatting Prompt

Format the supplied Thai text into clean Markdown novel prose. Output only the
formatted text.

Rules:
- Preserve every word, sentence, meaning, and story beat. Do not translate,
  summarize, rewrite, add, or remove content.
- Keep one blank line between normal paragraphs and separable dialogue,
  internal thought, scene breaks, and standalone sound effects.
- Keep dialogue visually clear and preserve the source speaker flow.
- Keep internal thoughts visually distinct when the input marks them.
- Keep system-like or ability text as a separate readable block when the input
  clearly presents it as such.
- Do not add English glossary terms, explanations, headings, or
  meta-commentary.
- Do not over-split ordinary narrative into decorative fragments.
- Do not create a chapter title or duplicate a title already in the input.

Text to format:
{{text}}
