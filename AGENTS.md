# AGENTS.md

Behavioral guidelines to reduce common LLM coding mistakes in Codex. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## Canonical Project Files

For this workspace, the project-level control files live at `D:\Fogust\Workspace\Novel`:

- `AGENTS.md`: work policy and behavior rules.
- `PROJECT_BRAIN.md`: durable project memory, current state, risks, and guardrails.
- `IMPLEMENT_PLAN.md`: active roadmap and next milestones.
- `ARCHITECTURE.md`: system structure, boundaries, flows, and ownership.
- `HERDR_WORKER_PROTOCOL.md`: bounded handoff rules for coding-agent workers; it does not define translation/provider behavior.

Novel-specific folders such as `Deep Sea Embers` may keep short compatibility stubs for older tools, tests, or dashboard links. Do not put durable cross-novel planning content in a single-novel folder.

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
- If a final output is truncated, contains runaway repeated characters, or has missing content, rerun the affected block from the earliest broken stage instead of manually patching around the loss.
- When a quality issue is fixed, record the cause and prevention mechanism in the project brain or implementation plan if it can recur.

### Major-Run Spot-Check Checklist

After every multi-chapter translation batch, broad repair pass, or MoonRead publication update:

- Confirm latest run status has no current failed blocks, no unresolved manual prompt, and no unexpected chapter-range expansion.
- Run deterministic output guardrails for the touched range before relying on human reading.
- Sample at least five chapters: first, last, early-middle, late-middle, and one chapter with known recovery/provider incident if any.
- In each sampled chapter, inspect the title, opening, middle passage, ending, paragraph density, dialogue/thought formatting, glossary/name consistency, and obvious omission/truncation.
- If MoonRead content changed, regenerate chapters and run reader lint/build/smoke before claiming it is ready.
- If the sample exposes a repeated pattern, repair the full affected range and add or extend a guardrail instead of treating it as a one-off.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.
