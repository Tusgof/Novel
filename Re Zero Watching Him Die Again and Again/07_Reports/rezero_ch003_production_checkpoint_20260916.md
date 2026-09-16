# Re:Zero ch003 Production Checkpoint

- Date: 2026-09-16
- Run: `rezero-ch002-ch003-production-v2`
- Scope: `ch003`
- Output: `05_Output/ch003/ch003.md`
- Published title: `บทที่ 3: ตอนที่ 2 ไดเรกเตอร์คัต`

## Final State

- Blocks complete: `11/11`
- Current failed blocks: none
- Manual actions: none
- Force-accept: none
- Output quality guardrails: passed
- Inspector Sentinel: blocker/major/minor/info `0/0/4/0`
- MoonRead generated Sentinel: blocker/major/minor/info `0/0/0/0`
- The four inspector minor findings are intentional source-backed media/version names: `Redo`, `Styx Helix`, `Acoustic Version`, and `Director's Cut`.
- MoonRead `publish:verify`, lint, build, smoke, and rendered-page inspection passed.

## Recovery Evidence

- `ch003-block-009` originally hard-failed because the literal artifact covered only 42.1% of the source.
- The block was rerun from translation. The accepted literal covers 17,055 of 17,251 source characters, or 98.9%, and preserves the source ending.
- `ch003-block-003` was rerun from formatting after post-format Re:Zero repairs were added. The accepted artifact contains no rejected `เอมิเลา`, preserves `เอมิเลีย`, `อัญมณี`, both `แม่มดแห่งความริษยา` occurrences, and explicit profanity.
- No final artifact was force-accepted or manually patched around truncation.

## Timing

| Metric | Value |
|:--|--:|
| Chapter wall time | 19,684.9 s (5 h 28 m 4.9 s) |
| Captured provider time | 7,043.0 s (1 h 57 m 23.0 s) |
| Failed provider time | 5,431.9 s (1 h 30 m 31.9 s) |
| Retry provider time | 3,149.9 s (52 m 29.9 s) |
| Retries | 2 |
| Failures | 17 |
| Timing coverage | 39 timed records / 94 provider calls |

Captured stage/provider time:

- translating/openrouter: 135.7 s
- refining/openrouter: 5,997.2 s
- qa/openrouter: 16.2 s
- formatting/openrouter: 893.9 s

The wall clock includes human waits and recovery gaps. This chapter started before full timing telemetry was available, so it is a partial-coverage sequential baseline rather than a clean normal-time estimate. Use `ch004+` for the first full-coverage per-chapter timing comparison.

## Next Safe Action

Prepare glossary and translated title sidecars for `ch004-ch010` sequentially, freeze glossary mutation, then run at most two chapter-isolated workers with separate run IDs and publish accepted chapters in order.
