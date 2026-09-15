# Re:Zero ch001 Production Pilot Checkpoint

Date: 2026-09-15
Run: `rezero-ch001-production-pilot-v1`

## Result

- `ch001` completed all 3 blocks and final assembly.
- Current failed blocks: none.
- Manual actions: none.
- Output guardrail: passed for `ch001`.
- Blocking Sentinel rerun: blocker/major/minor/info `0/0/0/0`.
- Independent advisory Sentinel: `0/0/1/0`; the only minor was the intentional acronym `OVA` in the author's spoiler notice.
- Final title: `บทที่ 1: คำทักทาย - ฉบับปรับปรุง`.
- Final output: 70,055 characters, 959 paragraphs, maximum paragraph length 599 characters.
- Source body: 75,697 characters; output/source character ratio 0.925.

## Incidents And Recovery

- DeepSeek refinement timed out on blocks 1 and 3; configured Gemini fallback completed those attempts.
- QA found omitted spoiler/mental-voice content in block 1 and omitted dialogue, author-note content, and a meaning inversion in block 3. The pipeline reran refinement and used its existing literal-safe recovery where required. All final QA artifacts passed without force-accept.
- DeepSeek formatting timed out on block 1. Gemini formatting changed content and was rejected, so deterministic local formatting preserved the verified refined text. Blocks 2 and 3 used validated Gemini formatting.
- Initial Sentinel was blocked because an approved pronoun-policy note in `01_Glossary` was incorrectly parsed as a glossary term. Sentinel now ignores approved notes that contain neither `original_term` nor `thai_term`; a regression test covers the case.

## Prevention Before ch002

The 5,000-word block size produced repeated timeout and omission pressure. The novel-specific `non_chinese_word_limit` is reduced to 3,000 words before any new chapter plan is created. The next run must verify its planned block identities after scan-only and before translation.

## Next Safe Action

Run preflight, then a scan-only glossary gate for `ch002-ch003` under a new bounded run ID. Do not publish until both chapters pass output guardrails, blocking Sentinel, and Inspector spot-checks.
