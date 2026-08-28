# Chinese-to-Thai Language Playbook

Layer: 1 (language-level, shared across novels)
Scope: Chinese web-novel source translated to Thai

## Setup Gate

- Read source as UTF-8 and reject replacement-character/mojibake output before glossary scan.
- Confirm chapter IDs, source titles, and body text come from the same raw chapter.
- Sample from the verified raw pool, not from already translated output.
- Keep novel-specific names, titles, pronouns, and source-site quirks in the novel vault.

## Titles And Names

- Translate every named Chinese chapter title through the title literal/refinement routes.
- Store a validated `04_Work/<chapter>/title.json` sidecar before final assembly.
- Preserve Arabic chapter numbers in Thai reader output; do not copy Chinese chapter markers into the body.
- Treat short Chinese strings as ambiguous: distinguish a person, place, organization, rank, technique, artifact, and ordinary noun before approval.
- Do not invent a surname, honorific, or lore meaning when the source does not provide one.

Example:

`第1章 修炼开始` -> `บทที่ 1: เริ่มต้นฝึกตน`

## Glossary And Voice

- Scan each bounded batch before translation and show exactly three safe Thai candidates for new terms.
- Reject source-script fallback text, provider/meta text, and generic terms that do not need stable translation.
- Prefer one approved Thai form; record aliases and rejected variants instead of creating duplicate notes.
- Keep register consistent with the novel profile. Use elevated diction for cultivation fiction, but do not force archaic pronouns into ordinary narration.
- Resolve pronouns from speaker, relationship, and point of view; never let a provider choose randomly between `ผม`, `ฉัน`, `เธอ`, and `คุณ`.

## Formatting Expectations

- Preserve dialogue, internal thought, system/UI text, skills, ranks, sound effects, and paragraph boundaries as separate source beats.
- Apply AI formatting only after QA, then validate Markdown deterministically.
- Keep dialogue readable with consistent paragraph spacing; use `**ข้อความ**` for bold and `*ข้อความ*` for italics when the reader surface requires emphasis.
- Never let formatting cleanup remove, merge, or invent a source beat.

## Common Failure Modes

- False negative: a compact name or title is treated as ordinary prose and is omitted from the glossary.
- False positive: a short substring is matched inside a longer word or phrase; use longest-match and boundary-aware matching.
- Leakage: Chinese text, pinyin, English provider commentary, or glossary notes appears in final Thai body text.
- Drift: one approved term receives multiple Thai variants across chapters; compare final output against approved notes.
- Truncation: a refined paragraph ends abruptly or loses a poem, thought, sound effect, or author note; rerun from the earliest broken stage.

## Required Checks

- Output guardrails: no Han Chinese in body text, no provider/meta markers, no unsafe encoding, no unintended Thai numerals, no missing title sidecar, and no known rejected glossary variants.
- Sentinel: run scoped to the touched chapters and block on glossary coverage, omission, title/name drift, truncation, or source-script leakage.
- Spot-check: inspect title, opening, middle, ending, paragraph density, dialogue/thought formatting, and glossary consistency.

## Feedback Loop

1. Record a repeated language-level defect here with a small example.
2. Keep a story-specific exception in that novel's profile or glossary.
3. Promote a proven cross-language rule to the shared multi-novel guardrail.
