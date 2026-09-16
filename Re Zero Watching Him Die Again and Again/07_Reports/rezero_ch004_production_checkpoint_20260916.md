# Re:Zero ch004 Production Checkpoint

- Date: 2026-09-16
- Run: `rezero-ch004-production-v1`
- Scope: `ch004`
- Output: `05_Output/ch004/ch004.md`
- Published title: `บทที่ 4: ตอนที่ 3 ฉบับผู้กำกับ`

## Final State

- Blocks complete: `10/10`
- Current failed blocks: none
- Manual actions: none
- Force-accept: none
- Output quality guardrails: passed
- Inspector Sentinel: blocker/major/minor/info `0/0/4/0`
- MoonRead generated Sentinel: blocker/major/minor/info `0/0/0/0`
- The four Inspector minor findings are intentional source-backed terms: `NPC`, opening theme `Redo`, ending theme `Styx Helix`, and `Reddit` in the author's note.
- Opening, middle, ending, title, paragraph density, Markdown emphasis, glossary terms, and the recovered blocks `002`, `005`, `007`, and `008` were inspected.
- MoonRead scoped `publish:verify`, lint, build, and smoke passed.

## Provider Recovery

- Refinement timed out on blocks `002`, `005`, and `008`; configured fallback recovery produced valid refined artifacts.
- Block `007` refinement exhausted the provider output limit and returned an empty assistant message; configured recovery succeeded.
- QA retries occurred on blocks `002`, `005`, and `008`; all passed without force-accept.
- Historical provider failures remain in the ledger as evidence, but no current failed block remains.

## Timing

| Metric | Value |
|:--|--:|
| Chapter wall time | 7,964.85 s (2 h 12 m 44.85 s) |
| Captured provider time | 4,673.23 s (1 h 17 m 53.23 s) |
| Failed provider time | 1,776.49 s (29 m 36.49 s) |
| Retry provider time | 925.13 s (15 m 25.13 s) |
| Retries | 3 |
| Historical failed attempts | 5 |
| Timing coverage | 50 timed records / 51 provider calls |

Stage/provider time:

- translating/openrouter: 536.95 s
- refining/openrouter: 3,563.19 s
- qa/openrouter: 50.75 s
- qa/openrouter_reasoning: 109.74 s
- formatting/openrouter: 412.60 s

## Orchestration Incident

The prep-only worker completed the glossary-scan gate, but the Inspector did not issue the body order immediately. Body translation therefore remained idle until the user asked for status. This was an orchestration failure, not provider latency.

Prevention is now part of `HERDR_WORKER_PROTOCOL.md`: before each multi-order `START`, record the expected next phase; after every `RETURN`, immediately issue the next bounded order, begin acceptance/publication, or record a concrete blocked state. Prep completion never counts as chapter completion.

## Next Safe Action

Push the verified MoonRead publication, verify the production `ch004` URL, then review and approve `ch005-ch010` glossary gates before starting at most two chapter-isolated body workers.
