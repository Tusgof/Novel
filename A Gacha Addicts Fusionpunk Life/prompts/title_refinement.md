You are refining Thai web-novel chapter titles.

Keep contemporary first-person titles in ผม (not ข้า); Count is เคานต์.

Return JSON only. No Markdown, no commentary.

Rules:
- Keep the chapter number exactly as "บทที่ N: ..."
- Improve natural Thai phrasing while preserving the supplied English title meaning.
- Do not make the title longer than necessary.
- Return Thai title text without adding source-script annotations or extra lore.
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
