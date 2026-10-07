# TDU Lean `ch011-ch020` Provider-Stop Checkpoint

## Decision

- **Measured status:** stopped and blocked by the explicit provider-failure stop rule.
- **Scope:** Ten Day Ultimatum (`ten-day-ultimatum`), exactly `ch011-ch020`.
- **Runtime:** Lean bounded batch; no migration work was included.
- **Publication:** no chapter from this continuation was promoted to `05_Output`; MoonRead generation and publish were not run.
- **Resume:** do not resume automatically. Verify provider health first, then issue a new bounded start for the same range.

## Boot and scope evidence

- Yuehua doctor after the stop: `fail=0`, `unverified=0`, `warn=1`; the only warning is the existing absolute-path portability finding in 397 files.
- Selected branch: `main`; current HEAD remained `eb60c7e` before the checkpoint edits.
- Post-stop TDU preflight: `degraded` only because the repair WIP is dirty; all configured provider executables were detected as ready.
- The dry-run locked 10 chapters and 44 blocks. Source character counts were: `ch011 2481`, `ch012 2221`, `ch013 2690`, `ch014 2298`, `ch015 2294`, `ch016 2304`, `ch017 2332`, `ch018 2526`, `ch019 2661`, `ch020 2164`.
- The canonical XSZJ `strip_site_footer()` cleanup removed 126 characters from each of `ch011`, `ch012`, `ch014`, `ch017`, `ch018`, `ch019`, and `ch020`; it removed 0 characters from `ch013`, `ch015`, and `ch016`. Metadata, titles, URLs, and chapter IDs were unchanged, and the cleanup is idempotent.

## Bounded attempts

| Run | Measured result | Evidence |
| --- | --- | --- |
| `TDU-LEAN-PROD-20261007-ch011-020` | `ch011` quarantined at QA because the uncleaned XSZJ footer left CJK characters; no final output | `ch011/chapter_result.json` |
| `TDU-LEAN-PROD-20261007-ch011-020-r1` | `ch011-ch012` staged; `ch013` quarantined for copied CJK puzzle annotations; interrupted before `ch014` completed | per-chapter checkpoints |
| `TDU-LEAN-PROD-20261007-ch011-020-r2` | `ch011-ch018` reached staged/QA-passed checkpoints; `ch019` had no result when the run was interrupted; `ch020` was not reached | `r2/chapter_result.json` files |

The r2 run was interrupted immediately after detecting the provider failure. No `lean_run_report.json` exists for these incomplete attempts, and `05_Output` still contains only the previously accepted `ch001-ch010` range.

## Repairs applied during the process

- Lean now applies the existing source-script annotation repair before QA.
- A TDU-only deterministic repair table records the observed source-backed name, pronoun, and typo variants found in the failed chapters; repairs are written into the refinement checkpoint and never force-accept QA.
- The staged-output spot-check then found two additional source-backed `ch017` variants: `ฉีเซี่ยี่ตาลง` → `ฉีเซี่ยหรี่ตาลง` and `ฉีเซี่ยืนอยู่` → `ฉีเซี่ยยืนอยู่`. Both are now covered by the same TDU repair table.
- Regression coverage is in `test_workspace_routing.py`; `python -m unittest -v test_workspace_routing.py test_xszj_adapter.py` passed all 22 tests. `python -m compileall -q novel_pipeline` and `git diff --check` also passed.

## Provider stop evidence

The completed r2 chapter metadata records the same failure on the configured `openrouter_reasoning` QA route: the OpenRouter shim returned an empty assistant message with `finish_reason=length`, `native_finish_reason=length`, and `completion_tokens=4096`. The configured fallback made each affected chapter QA-pass, but the user stop rule treats the provider failure itself as a stop. The process was stopped while `ch019` was beginning literal translation; no new provider run was started afterward.

## Resume attempt after owner continuation

- `preflight` was `ready`, and the explicit dry-run again confirmed exactly `ch011-ch020` / 44 blocks.
- `--resume` reused the existing checkpoints for `ch011-ch018`; the new deterministic repair was visible in staged `ch017` (`ฉีเซี่ยหรี่ตาลง`, `ฉีเซี่ยยืนอยู่`).
- The process reached `ch019` only after `ch018` completed, then was stopped when `ch018/chapter_result.json` again recorded the same `openrouter_reasoning` provider failure. `ch019` has no result and no final output; no run report or promotion was created.
- Rechecked the available staged range after the repair: output guardrails passed and Sentinel remained `0 blocker / 0 major / 0 minor / 0 info`. New evidence: `07_Reports/sentinel_quality_TDU-LEAN-PROD-20261007-ch011-020-r2-resume-staged_20261007_054754.md` and its JSON companion.

A further owner-requested retry of the same bounded `r2 --resume` was attempted after a clean doctor/preflight/dry-run. It again reused `ch011-ch018`, reached the start of `ch019`, and stopped on the identical `ch018` provider failure. `ch019` still has no result, so the accepted state and publication decision are unchanged.

## Quality checks on the partial staged range

- Deterministic guardrails on the staged candidates `ch011-ch018`: **passed**.
- Scoped staged Sentinel `ch011-ch018`: **0 blocker / 0 major / 0 minor / 0 info**. Evidence: `07_Reports/sentinel_quality_TDU-LEAN-PROD-20261007-ch011-020-r2-staged_20261006_185435.md` and its JSON companion.
- Inspector spot-check covered five available staged chapters: `ch011`, `ch012`, `ch013`, `ch017`, and `ch018`. Titles, opening/middle/ending structure, paragraph density, dialogue markers, and CJK/meta leakage were inspected. `ch017` exposed the two variants recorded above and is therefore not treated as publish-ready evidence. `ch020` was unavailable because the provider stop occurred first.

These partial checks do not satisfy the final `ch011-ch020` production gate. The full-range guardrails, final Sentinel, five-chapter acceptance sample including `ch020`, MoonRead regeneration, reader lint/build/smoke, and publication remain pending.

## Next safe action

Restore and verify the failing provider route or its authorized fallback, then issue a fresh bounded continuation for exactly `ch011-ch020`. Reuse only hash-matching checkpoints, rerun the corrected `ch017` path, complete `ch019-ch020`, and require final guardrails, blocking Sentinel, spot-check, and MoonRead checks before any promotion or publish.
