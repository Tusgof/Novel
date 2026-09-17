# Re:Zero ch008 Production Checkpoint

- Date: 2026-09-17
- Run: `rezero-ch008-production-v1`
- Scope: `ch008`
- Output: `05_Output/ch008/ch008.md`
- Published title: `บทที่ 8: ตอนโอวีเอ 1 เมมโมรีสโนว์`

## Final State

- Blocks complete: `10/10`
- Current failed blocks: none
- Manual actions: none
- Force-accept: none
- Output quality guardrails: passed
- Runtime Sentinel: blocker/major/minor/info `0/0/0/0`
- Inspector Sentinel: blocker/major/minor/info `0/0/8/0`
- The eight minor findings are source-backed OVA/title, song, video-id, and author-note references: `OVA`, `Re:Zero`, `Vida`, `watch`, `CcfrahkdGmM`, `What`, `Greed`, and `Gluttony`.
- Title, opening, middle, ending, paragraph density, Markdown emphasis, glossary terms, and recovered blocks `003-004` were inspected.
- MoonRead scoped `publish:verify`, lint, production build, and smoke passed; generated Re:Zero scope is `ch001-ch008`.

## Recovery Evidence

- Block `003` recovered from prompt leakage and the rejected Anastasia spelling before completion.
- Block `004` recovered an invented title card to the source-backed `Re:Zero - รีเซทชีวิต ฝ่าวิกฤติต่างโลก`.
- Refinement provider timeout/length incidents in later blocks used the configured fallback routes. Thirteen historical failed attempts remain in the ledger, but none is a current failure.
- Formatting validators rejected provider output that changed content and used the deterministic local fallback where required.

## Prevention

- Rejected glossary variants that overlap approved Thai terms use boundary-aware matching, preventing false repair of `อนาสตาเซีย โฮชิน`.
- Truncated or empty provider output remains blocking and must rerun from the earliest broken stage; no force-accept was used.
- Chapter acceptance remains sequential even while separate chapter workers may execute concurrently.

## Timing

| Metric | Value |
|:--|--:|
| Chapter wall time | 53,017.1 s |
| Captured provider time | 6,725.3 s |
| Failed provider time | 3,921.7 s |
| Retry provider time | 2,376.9 s |
| Retries | 16 |
| Historical failed attempts | 13 |
| Timing coverage | 60 timed records / 72 provider calls |

Stage/provider time:

- translating/openrouter: 644.0 s
- refining/openrouter: 4,806.8 s
- qa/openrouter: 74.5 s
- qa/openrouter_reasoning: 60.5 s
- formatting/openrouter: 1,139.5 s

The wall time includes a long session gap and is not a clean throughput measurement. Provider time remains usable for stage-cost comparison.

## Next Safe Action

Publish and verify `ch008`, then recover `ch009-block-004` from `translate` before resuming `ch009-block-005` through `ch009-block-012`.
