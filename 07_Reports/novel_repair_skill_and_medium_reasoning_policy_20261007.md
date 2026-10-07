# Novel Repair Skill and Medium-Reasoning Policy

Date: 2026-10-07

## Change

- Added `.agents/skills/novel-translation-repair/SKILL.md` for Worker-owned post-QA chapter-local recovery.
- The skill covers incident freeze, evidence-chain inspection, earliest-stage diagnosis, bounded repair, QA/guardrail/Sentinel verification, and an evidence-based `complete` or `blocked` return.
- It explicitly keeps provider routing, architecture, control documents, force-accept, and publication under Inspector authority.
- All six registered novel provider configs now default configured OpenRouter generation/refinement and QA routes to reasoning `medium`; QA routes use `12000` completion tokens.

## Basis

The repair workflow incorporates recurring incidents recorded in the repository, including empty provider output and `finish_reason=length`, quota/timeout failures, omission/truncation, source-script leakage, glossary/name/pronoun drift, refinement meaning drift, formatting defects, false QA rejection, and stale checkpoint reuse.

## Verification status

- Measured: skill validator, YAML/config loading, conflicting reasoning-flag checks, compile, tests, diff check, and six novel preflights are required before commit.
- Measured: no provider-backed production run is included in this change.
- Not yet measured: translation quality, latency, cost, and provider stability after switching all configured routes to reasoning `medium` and QA `12000`.

## Follow-up

Run a bounded provider-backed probe before resuming a long production window. Compare the new run with the prior evidence, keeping provider failures visible and stopping on global provider failure.
