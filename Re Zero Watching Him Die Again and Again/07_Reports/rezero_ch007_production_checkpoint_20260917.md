# Re:Zero ch007 Production Checkpoint

- Date: 2026-09-17
- Run: `rezero-ch007-production-v1`
- Scope: `ch007`
- Output: `05_Output/ch007/ch007.md`
- Published title: `บทที่ 7: ตอนที่ 6 ฉบับผู้กำกับ`

## Final State

- Blocks complete: `9/9`
- Current failed blocks: none
- Manual actions: none
- Force-accept: none
- Output quality guardrails: passed
- Inspector Sentinel: blocker/major/minor/info `0/0/4/0`
- The four minor findings are source-backed `Redo`, `Zarno102`, `ScuffedSenku`, and `Senku` references.
- Title, opening, middle, ending, paragraph density, Markdown emphasis, glossary terms, and recovered blocks `006-008` were inspected.
- MoonRead scoped `publish:verify`, lint, build, and smoke passed; generated scope is `ch001-ch007` with no missing or rejected chapter.

## Recovery Evidence

- Block `006` used `โล่แห่งสุสานศักดิ์สิทธิ์` for source `Shield of the Sanctuary`; it was repaired to the approved `โล่แห่งแซงชัวรี`, then passed QA without auto-refine.
- Block `007` contained one provider-inserted CJK character in an otherwise Thai sentence. The source-backed phrase was restored, and QA passed retry `0`.
- Block `008` mistranslated Subaru as Emilia's maid and inserted Arabic-script characters into `mabeast`. Both source-backed defects were repaired, and QA passed retry `0`.
- Block `009` completed normally. Historical provider failures and retries remain in the ledger but are not current failures.

## Prevention

- Rejected glossary variants that overlap their approved Thai term are no longer repaired or blocked using ambiguous substring matching. The Layer 0 matcher and QA rule have regression coverage.
- `Anastasia Hoshin` keeps the approved `อนาสตาเซีย โฮชิน`; its rejected full-name spelling is recorded without matching across Thai word boundaries.
- Runtime Sentinel report paths must be included in future HERDR assembly orders because assembly creates those reports by design.

## Timing

| Metric | Value |
|:--|--:|
| Chapter wall time | 15,124.7 s |
| Captured provider time | 7,857.9 s |
| Failed provider time | 4,656.5 s |
| Retry provider time | 4,514.5 s |
| Retries | 23 |
| Historical failed attempts | 16 |
| Timing coverage | 62 timed records / 80 provider calls |

Stage/provider time:

- translating/openrouter: 737.7 s
- refining/openrouter: 5,328.9 s
- qa/openrouter: 73.1 s
- qa/openrouter_reasoning: 191.9 s
- formatting/openrouter: 1,526.2 s

## Next Safe Action

`ch007` is live at pushed commit `6b0fc2c`. Continue and independently accept the already-approved, chapter-isolated `ch008` run before publication.
