# AGENTS.md

Behavioral guidelines to reduce common LLM coding mistakes in Codex. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## Canonical Project Files

For this workspace, the project-level control files live at the repository root:

- `AGENTS.md`: work policy and behavior rules.
- `PROJECT_BRAIN.md`: durable project memory, current state, risks, and guardrails.
- `IMPLEMENT_PLAN.md`: active roadmap and next milestones.
- `ARCHITECTURE.md`: system structure, boundaries, flows, and ownership.
- `.agents/skills/novel-verify/SKILL.md`: how to verify work on its real surfaces (output, Sentinel, MoonRead) and the Feature Map of every workspace feature with its commands and gotchas. Read it before claiming translation, repair, glossary, setup, or publication work is done.
- `.agents/skills/novel-translation-repair/SKILL.md`: Worker-owned post-QA diagnosis, bounded recovery, and verification. Read it for chapter-local repair orders.
- `.yuehua-kit.json`: Yuehua Kit v4.0 adoption record (UNIT, T2). Start non-trivial work with the `yuehua-mode` skill: run its bundled `doctor` first, restate the task, pick a playbook, verify on the real surface, and land through `yuehua-land` (done means merged to `main` with the `tests` CI green on the merged commit; report claims as measured, inferred, or guessed).
- `HERDR_WORKER_PROTOCOL.md`: bounded Inspector/Worker handoff rules, including explicitly authorized translation-pipeline execution; it never overrides provider routing or quality policy.

Novel-specific folders such as `Deep Sea Embers` may keep short compatibility stubs for older tools or links. Do not put durable cross-novel planning content in a single-novel folder.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" -> "Write tests for invalid inputs, then make them pass"
- "Fix the bug" -> "Write a test that reproduces it, then make it pass"
- "Refactor X" -> "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] -> verify: [check]
2. [Step] -> verify: [check]
3. [Step] -> verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

## 5. Translation Output Quality Guardrails

**For novel work, final Markdown is product surface. Treat it as code.**

- Before claiming a translation or reader fix is done, run the project output guardrail if one exists.
- Do not rely only on provider QA for name consistency, pronoun consistency, paragraph density, or Markdown rendering.
- Prefer low-risk deterministic repairs for approved terminology, repeated known variants, paragraph reflow, and reader rendering bugs.
- If a final output is truncated, contains runaway repeated characters, or has missing content, quarantine that chapter and rerun it from the earliest broken stage instead of manually patching around the loss. Continue later chapters within the authorized range when their inputs and worker state remain healthy.
- When a quality issue is fixed, record the cause and prevention mechanism in the project brain or implementation plan if it can recur.
- For post-QA chapter-local recovery, the Worker follows `.agents/skills/novel-translation-repair/SKILL.md`; the Inspector retains policy, routing, scope, and final acceptance.

### Major-Run Spot-Check Checklist

After every multi-chapter translation batch, broad repair pass, or MoonRead publication update:

- Confirm latest run status has no current failed blocks, no unresolved manual prompt, and no unexpected chapter-range expansion.
- Chapter-local failures may remain quarantined while a major run continues; verify they are listed with evidence and are not promoted or published.
- Run deterministic output guardrails for the touched range before relying on human reading.
- Sample at least five chapters: first, last, early-middle, late-middle, and one chapter with known recovery/provider incident if any.
- In each sampled chapter, inspect the title, opening, middle passage, ending, paragraph density, dialogue/thought formatting, glossary/name consistency, and obvious omission/truncation.
- If MoonRead content changed, regenerate chapters and run reader lint/build/smoke before claiming it is ready.
- If the sample exposes a repeated pattern, repair the full affected range and add or extend a guardrail instead of treating it as a one-off.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.

## Yuehua Kit v4 Contract

This repository adopts Yuehua Kit v4.0.5 as a `UNIT` at tier `T2`. The verified release commit is pinned in `.yuehua-kit.json`; the stronger novel-specific rules above remain in force. This adoption changes only this repository; its six child novels retain the registry, product routes, and quality gates.

Use `yuehua-mode` and `yuehua-land` from the pinned release. Check installed `INSTALLED_FROM.json` against the lock; if it is older, follow the verified tag checkout's skills and CLI outside this repository instead of inheriting stale policy. See the Feature Map's [kit adoption checks](.agents/skills/novel-verify/references/features/kit-adoption.md). Shared user-level skills require separate approval to update; an installer dry-run is not permission to install.

### Work From The Goal And The Check

- Restate the goal, scope, and definition of done before acting.
- State assumptions and surface ambiguity instead of guessing.
- Prefer the smallest change that works; do not add speculative layers, schemas, or configuration.
- Report out-of-scope findings as backlog instead of doing them silently.

### Verify Where The Work Lands

- Start non-trivial work by running the Yuehua doctor on the default branch.
- A red default branch must be fixed, redesigned, or retired by a recorded decision; it must never be ignored.
- Tests are necessary but not sufficient. Verify the real product surface, including translated output, Sentinel, and MoonRead where applicable.
- Never weaken a test, validator, or gate to get green.
- If a check cannot run, report it as unverified rather than passing it by assumption.

### Claims, Completion, And Authority

- Label claims as measured, inferred, or guessed.
- Work is complete only when merged to the default branch with CI green on the merged commit, or parked by a recorded decision.
- Report partial completion as the exact done and not-done items; never imply that an unfinished scope is complete.
- The owner must approve a merge; an agent must not self-approve. T3 work also requires the named independent reviewer.
- Do not stop for reversible actions. Stop before spending money, publishing, production writes, deletion, credentials, or locked gates unless authority is explicit.
- Technical access, a logged-in browser, full access, or a skipped prompt is not authority by itself.
- Locked decisions and gates change only through their approval process. Keep decision logs append-only; record reversals as superseding decisions with reasons.

### Secrets, Vaults, And Provenance

- Never put secrets in the repository, logs, reports, prompts, routines, work orders, or worker handoffs. Reference environment-variable or secret names only. A discovered secret is an EXPOSURE finding: stop, report, and ask the owner to revoke it.
- Keep payroll, contracts, personal data, financial statements, legal documents, and other vault-class material outside the working repository, referenced by pointer. Finding vault material in the repository is an EXPOSURE finding and must be flagged immediately.
- Do not change repository visibility without the required pre-publication scan.
- Record money, accounts, and data purchases with true provenance. Do not misrepresent an account or identity.
- Before using a credential, confirm that it is registered for this unit and within its cap.
- In public repositories, use the identity already present in the repository history; do not introduce a personal email.

### Portability And State

- Do not add absolute machine paths to code, configuration, or durable control documents; use commands or named environment variables.
- Declare dependencies, pin runtime versions, and make CI install exactly what the repository needs.
- Project state must be reproducible from versioned repository files, not from a browser session, personal cloud storage, or agent memory.

### Browser Work

- Read the pinned, tool-neutral [agent-browser policy](policies/agent-browser.md) before agent-driven browser work. Select a suitable available API, CLI, or browser tool; no browser product is required or preferred. Playwright remains the declared hermetic reader-test surface, not a default for signed-in work.
- Verify the actual product, version, connection, profile, and task authority at runtime; discover endpoints and schemas from the active tool rather than hard-coding installation paths or example ports.
- Preserve credential/resource registration, caps, vault handling, profile isolation, and observed-result evidence for every tool. Remote exposure requires an explicit bounded work order and a private tunnel by default; never commit or log an active control URL.
- OAuth grants and prompt-skipping with a signed-in profile or consequential action require explicit bounded authority. Technical access never widens the work order; inspect uncertain results before retrying an external write.
- Browser session history, screenshots, and extracted page data may be sensitive and stay out of the repository.

### Low-Reasoning Execution

- Before implementation, classify reasoning demand separately from T1/T2/T3. Read [execution-workers policy](policies/execution-workers.md): only settled, bounded low-reasoning implementation goes to `.opencode/agents/execution-worker.md` using `opencode-go/deepseek-v4.1-flash#low`, after resource/data, included-allowance/cap, native runtime, and effective-permission checks.
- Medium/high work, the main model, reviewers, and other agent/model assignments remain unchanged. The existing novel translation Worker and its HERDR approval/acceptance boundary are not replaced by the low-reasoning coding profile.
- If unavailable, quota-blocked, unverified, or unsuccessful, the main agent immediately takes over using its current model, reports why, confirms the worker stopped, and inspects partial work before editing the same files. Do not wait for owner input or retry indefinitely to choose a fallback.
- The lead owns decomposition, diff review, tests, integration, and existing approvals. Do not enable Extra Usage, top up credits, change privacy, add credentials, or substitute a different paid provider to keep delegation running. Without a safe native child-session path, use main-agent fallback.

**Working if:** the default branch is green or has a recorded decision, claims survive a clean-clone check, finished work is merged, and audits find no surprises.
