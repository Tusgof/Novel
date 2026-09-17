# Re:Zero ch009-ch010 Provider-Limit Checkpoint

- Date: 2026-09-17
- Published scope: `ch001-ch008`
- Live commit: `5e3fbfc303930711202465a3408321d66de35a43`
- Production URL checked: `ch008` returned HTTP `200` with its Thai title.

## ch009

- Run: `rezero-ch009-production-v1`
- Complete blocks: `5/12` (`001-005`)
- Current failed block: `ch009-block-006` at `translating`
- Final output: missing by design; the incomplete chapter was not published.
- Block `004` was rerun from `translate` after a truncated literal result and passed QA retry `0`.
- Block `005` was rerun from `translate` after QA proved that its literal artifact omitted the final sentence and two final paragraphs. The replacement formatted artifact is complete, contains no CJK leakage, and passed QA retry `0`.
- Block `006` exhausted its configured literal routes: OpenRouter rejected the 12,000-token request because the key lacked sufficient credit, the OpenRouter model fallback timed out, and the Codex fallback could not refresh its expired CLI session.

## ch010

- Run: `rezero-ch010-production-v1`
- Complete blocks: `1/19` (`001`)
- Current failed block: `ch010-block-002` at `qa`
- Final output: missing by design; the incomplete chapter was not published.
- Block `001` was rerun from `refine` after a provider inserted the CJK character `兑` into Thai prose. The replacement passed QA retry `0`, formatted successfully, and contains zero CJK characters.
- Block `002` has completed literal and refined artifacts. QA could not run because OpenRouter rejected the request for insufficient credit.

## Stop Decision

- No force-accept, token-ceiling reduction, routing change, manual output patch, chapter assembly, MoonRead generation, or publication was performed for `ch009-ch010`.
- The two-chapter execution window stopped after provider exhaustion as required.
- Existing artifacts and ledger evidence are resumable; do not restart either run from the beginning.

## Next Safe Action

1. Restore enough OpenRouter credit for the configured 12,000-token route and restore the Codex CLI login before relying on that fallback.
2. Rerun `ch009-block-006` from `translate`, inspect it, then resume `ch009-block-007` through `012`.
3. Rerun `ch010-block-002` from `qa`, inspect it, then resume `ch010-block-003` through `019`.
4. Accept and publish strictly in chapter order: `ch009` before `ch010`.
