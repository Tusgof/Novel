# Re:Zero ch005 Production Checkpoint

- Date: 2026-09-17
- Run: `rezero-ch005-production-v1`
- Scope: `ch005`
- Output: `05_Output/ch005/ch005.md`
- Published title: `บทที่ 5: ตอนที่ 4 ฉบับผู้กำกับ`

## Final State

- Blocks complete: `14/14`
- Current failed blocks: none
- Manual actions: none
- Force-accept: none
- Output quality guardrails: passed
- Inspector Sentinel: blocker/major/minor/info `0/0/7/0`
- The seven minor findings are source-backed names or titles: `Director's Cut`, `Redo`, `Myth`, `Roid`, `Straight Bet`, `Ao3`, and `What` from `What if`.
- Title, opening, middle, ending, paragraph density, Markdown emphasis, glossary terms, and recovered blocks `012` and `014` were inspected.
- MoonRead scoped `publish:verify`, lint, build, and smoke passed; generated scope is `ch001-ch005` with no missing or rejected chapter.

## Recovery Evidence

- Block `012` hit a deterministic rejected-variant false positive because `ออนาสตาเซีย` crossed the word boundary in `เมื่ออนาสตาเซีย`. The sentence was rewritten to `ครั้นอนาสตาเซีย`; QA then passed without auto-refine or force-accept.
- Block `014` contained one provider-inserted Chinese fragment (`只有`) inside an otherwise translated sentence. The source-backed phrase was repaired, QA passed retry `0`, and formatting completed.
- Historical provider failures and retries remain in the ledger. They are not current failures.

## Timing

| Metric | Value |
|:--|--:|
| Chapter wall time | 15,333.9 s |
| Captured provider time | 9,169.0 s |
| Failed provider time | 5,126.7 s |
| Retry provider time | 3,805.7 s |
| Retries | 17 |
| Historical failed attempts | 21 |
| Timing coverage | 99 timed records / 103 provider calls |

Stage/provider time:

- translating/openrouter: 765.8 s
- refining/openrouter: 7,249.9 s
- qa/openrouter: 135.5 s
- qa/openrouter_reasoning: 350.6 s
- formatting/openrouter: 667.2 s

## Next Safe Action

Publish and verify `ch005`, then accept `ch006` only after its independent gates pass.
