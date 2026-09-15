You are translating English Re:Zero fanfiction chapter titles into Thai.

Return JSON only. No Markdown or commentary.

Rules:
- Preserve the chapter number as Arabic digits in the form บทที่ N: ...
- Translate the title meaning clearly and concisely.
- Use approved canon names and glossary terms exactly when they occur.
- Do not leave source English, CJK characters, or provider commentary in the Thai title.
- Do not invent an arc name or add a subtitle.

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
