# TDU Code ch026-ch030 — Inspector acceptance

## Scope and authority

Owner authorized Code translation of exactly ch026-ch030 using a subagent, with
Inspector-owned terminology/acceptance. Code is the existing Lean engine using
the Go Haiku/DeepSeek route selection, not a separate translation engine. Reading
is **local only**; the earlier public publication plan was superseded during the
OpenCode question round after confirming the repository and live reader are public.
No new content push, deploy, account change, Extra Usage, or $30 experiment ran.
Included quota and Extra Usage OFF are owner-reported, not independently measured.

## Measured accepted state

- Run `CODE-TDU-PROD-20261108-ch026-030`: complete, five promoted, no quarantined
  chapter or unresolved manual prompt. Worker session stopped before acceptance.
- Original raw source for each chapter matches the primary workspace byte for
  byte. The raw files were preserved; historical site footers in ch026/ch028 were
  excluded from translated story output with traceable checkpoint repairs.
- Fresh post-repair QA passes all five. Independent output guardrails pass;
  final Inspector Sentinel is blocker/major/minor/info **0/0/0/0**, including
  advisory English checks, not just the runtime skip-advisory gate.
- The batch-specific acceptance checker recomputes literal/refinement/QA/format/
  harvest dependency hashes against the unchanged inputs. All five match; final
  and staged files match. It reconstructs the exact authorized prose repairs from
  byte backups and confirms no other passage changed. All 36 backup checksums pass.
- Inspector source-backed reading covered every chapter's title, opening,
  middle, ending, dialogue/thought layout, quantities, names and pronouns. Reviewed
  the sword inscription/death clue, token allocation/false accusation, echo and
  disappearing display, and one-person/five-minute warehouse-game conditions.

## Why another acceptance cycle was needed

The first Worker return had green QA/guardrails but still varied Qi Xia's own
voice across chapters, used male-address wording toward women, changed one sword
name between translation/transliteration, and drifted from the accepted animal
roles and echo sentence in previous chapters. Green per-chapter QA was therefore
not sufficient for cross-chapter acceptance.

The Inspector supplied one prevalidated, source-backed plan. A separately bounded
Worker cycle preserved the initial evidence, applied only attributed paragraph
and unambiguous term corrections to refined checkpoints, then reran normal QA,
formatting, harvest, staged Sentinel and promotion. No final-only patch or
force-accept occurred; upstream input hashes were not forged. Existing literal,
source, glossary, prompt, provider configuration and title inputs stayed frozen.

For recurrence prevention, `02_Database_Views/Code Continuity ch026-ch030.md`
records the accepted identities/voice/clues, and the batch-scoped acceptance
checker under the private order directory is required before reader assembly.
Broader source-footer preprocessing and long-run voice tuning remain future
bounded work, not silently promoted shared policy. Historical chapters are not
rewritten by this order.

## Final output hashes

| Chapter | Title | SHA256 |
| --- | --- | --- |
| ch026 | ผู้ตาย | `5a2811d5257726a8233082245995a5ace192c9925076eb5f96c3d51f01cac502` |
| ch027 | ความโง่เขลา | `bb5b9e1e0a49374059f94e9d6559fcd78a7f762fad958129d7dcacdb8b535ef6` |
| ch028 | แยกทางกัน | `d63d07c732ea2fe275319f8b7e0fbcf12d2def2528e24e08f871fb50dfef329c` |
| ch029 | ปริศนา | `dcaa7e87647c74be1b2e71b7cb0636bc7230e1547fbdbf14bf139e40018a5d7c` |
| ch030 | มนุษย์หนู | `73ba5089aa922ed35d2e4a5f29db6446d5fe18fe08adb773cff2b0b1cf189b8f` |

These accepted outputs and exact run artifacts were copied into the primary
workspace only at new paths. The imported run preserves its original execution
context; `import-context.json` explains why moving context is not authority to
rewrite cache hashes or resume under a different workspace blindly. No existing
global last-title log or old run/ledger/output was overwritten.

## Measurement, not billing assumptions

Native stage traces: **57 provider-stage invocations**, zero recorded transport
failures. Counts include title preparation: 23 Haiku-low literal calls, six
DeepSeek-high refinement calls, 14 DeepSeek-high QA calls, three Haiku-high QA
adjudications, and 11 Haiku-low harvest calls. The initial Worker report's
“zero fallbacks” claim is superseded: three independent QA adjudications occurred.
Worker/orchestrator inference is separate and not included in the stage count.
Go allowance consumption and monetary cost remain unmeasured; native CLI cost=0
is not reported as free usage.

## Reader and delivery

The private reader lives under ignored `04_Work/_local_readers/Code-20261108/`.
Its own registry targets TDU ch001-ch030 and labels only ch026-ch030 `[Code]`;
ch001-ch025 keep `[Lean]`. Generation reports six books / 699 available / zero
missing / zero rejected. New generated chapters match accepted output. Public
reader files and the public registry remain unchanged at TDU ch001-ch025.

Final private lint, production build (716 generated routes) and desktop/mobile
browser smoke **passed**. The reader reports five Code chapters and correctly
renders ch026/ch030 at 1440px and 390px, with matching titles/labels, no duplicate
title or horizontal overflow, and zero unexpected console errors. Other sampled
Lean/Pipe pages keep their labels. Screenshots and JSON evidence are stored in
the private reader's `MoonRead/output/playwright/` directory. This verifies local
rendering, not public deployment or perfect literary quality.

No new commit/push/CI result or public publication is claimed by this local-only
delivery. The two Code-label reader script changes remain uncommitted in the
isolated branch/private reader, not in public main. Existing 121 dirty
primary-checkout files retain their original SHA256 values.

The separate Fusionpunk vault is an Inspector-prepared **source-pending draft**:
zero imported chapter bodies, zero translated chapters and no approved pilot.
It is not publicly registered and cannot pass production preflight yet.
