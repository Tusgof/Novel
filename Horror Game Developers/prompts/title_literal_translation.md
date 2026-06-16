You are translating English web-novel chapter titles into Thai.

Return JSON only. No Markdown, no commentary.

Rules:
- Preserve chapter numbering as Thai: "บทที่ N: ..."
- Translate the title meaning literally and clearly.
- Preserve part markers such as [1], [2], [3].
- Do not include source English in the Thai title unless it is a proper name that should remain transliterated.
- Mandatory glossary terms must be copied exactly into the Thai title when their source term appears.

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
