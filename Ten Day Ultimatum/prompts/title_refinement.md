You are refining Thai web-novel chapter titles.

Return JSON only. No Markdown, no commentary.

Rules:
- Keep the chapter number exactly as "บทที่ N: ..."
- Improve natural Thai phrasing while preserving the Chinese title meaning.
- Do not make the title longer than necessary.
- Do not include Chinese characters.
- Mandatory glossary terms must be copied exactly into the Thai title when their source term appears.
- Do not replace glossary terms with synonyms or deprecated variants.

Glossary:
{{glossary_subset}}

Input JSON:
{{title_payload}}

Output schema:
{
  "titles": [
    {"chapter_id": "ch001", "thai_title": "บทที่ 1: ..."}
  ]
}
