# IRS Translation Policy

Status: active

## Scope

Novel: `I'm an Infinite Regressor, But I've Got Stories to Tell`

This policy applies to translation, refinement, QA, formatting, Sentinel review, and MoonRead publication for IRS.

## Voice And Register

- Thai prose should be readable, dry, reflective, and slightly weary.
- Preserve the narrator's deadpan humor and accumulated fatigue from repeated failed regressions.
- Avoid wuxia, cultivation, nautical, or horror-game register unless the source explicitly invokes that flavor as parody or comparison.
- Keep first-person narration natural and consistent. Default narrator pronoun is `ผม` unless a local context clearly requires otherwise.

## Formatting And Pacing

- Preserve the source chapter's paragraph rhythm as much as possible.
- Do not aggressively split or merge paragraphs just to make the output look like another novel.
- Keep standalone source lines standalone when they are used for pacing, emphasis, dialogue beats, thoughts, title cards, or separators.
- Use one blank line between paragraphs in final Markdown.
- Formatting may add Thai quotation marks, italics, or bracket styling only when the semantic role is already clear from the text.
- Formatting must not rewrite, shorten, reorder, summarize, or add content.

## Early Glossary Watchlist

- Infinite Regression
- regressor
- regression
- anomaly
- Constellation
- administrator
- cycle / run

## Stop Conditions

Stop and inspect if any of these appear:

- narrator pronoun drifts between `ผม`, `ฉัน`, `เรา`, or slang register without source reason
- key terms are translated inconsistently across nearby chapters
- formatting collapses many short source beats into dense paragraphs
- provider output adds commentary, markdown fences, English leftovers, or missing source beats
- Sentinel reports blocker/major findings
