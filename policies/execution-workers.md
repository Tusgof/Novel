# Low-reasoning execution workers (K-025)

Delegate clearly specified low-reasoning implementation to **DeepSeek V4.1 Flash through OpenCode Go**. The responsible agent remains the lead and owns decomposition, review, verification, and integration. Medium/high reasoning stays with the responsible agent, with no new model or reasoning-setting assignment. This is independent of the unit's T1/T2/T3 risk tier; existing approvals and independent-review requirements remain in force.

## 1. Classify the actual task

Low means the requirements, approach, allowed files, and acceptance checks are already clear. The worker executes an established decision rather than making architectural, security, business, or acceptance decisions.

| Candidate category | Low only when |
|:--|:--|
| Routine Coding | The instructions and existing implementation pattern are explicit. |
| Feature Extension | The small extension follows an agreed interface without a new design or ownership boundary. |
| Boilerplate Generation | The structure and conventions are already selected. |
| Unit Test Generation | The lead supplies expected behavior and acceptance cases; the worker does not invent the oracle. |
| Bulk Code Modification | One specified transformation applies to an enumerated file set. File count alone does not decide reasoning level. |
| Sub-Agent Execution | The delegated task meets the same low criteria. Being a subagent does not make research, design, or review low. |

Keep unresolved design, ambiguous behavior, security/authority changes, root-cause investigation, and independent review with the responsible agent or the unit's existing reviewer. Split out a genuinely mechanical part only after the lead settles the decision. Do not route every subagent to the execution model.

## 2. Preflight and dispatch

1. The lead runs the unit boot checks, establishes the working-tree baseline, and classifies the bounded task. A worker reuses that baseline; it is not a second project owner or a recursive orchestrator.
2. Verify the exact Go model and `low` variant in the current catalog, native child-session support, and effective worker permissions. The checked-in OpenCode V2 profile is `.opencode/agents/execution-worker.md`; an installed `yuehua-mode` carries the same file at `assets/opencode/execution-worker.md`.
3. Apply the existing resource registry and data boundaries: the Go subscription must permit this unit and have room under its approved allowance/cap. Confirm that included quota remains and the request will not fall through to unapproved overage; an already enabled Extra Usage setting is not spending authority. Catalog availability and an owner's purchase are not proof of remaining quota or permission to send particular data. Keep secrets and vault material out of the handoff.
4. Dispatch one bounded work order with: goal; settled approach and examples; allowed files; baseline and existing work to preserve; expected behavior and checks; stop conditions; and return requirements. Do not edit the worker's assigned files concurrently.
5. The worker returns its status, changed paths, test evidence or explicit `not run`, uncertainties, and any partial changes. The lead checks the diff against the work order, runs the required tests/real-surface checks, and accepts or completes the work. A worker return is not an approval or a claim that the overall task is done.

Use the native `execution-worker` subagent when available. The profile selects the Go provider and `low` variant, not the main session's model. It allows in-workspace file reading/editing, denies shell, network/MCP, external-directory access, and recursive subagents, and protects control files. The lead therefore runs test commands and handles Git, CI, and external actions. File permissions are a baseline, not a dynamically generated per-work-order sandbox; use a separate worktree when isolation is needed and always review changed paths.

## 3. Main-agent fallback — continue immediately

If the model/provider/profile is unavailable, authentication or privacy policy blocks it, quota is exhausted, permitted usage cannot be confirmed, the harness cannot safely spawn it, or the worker errors, exceeds its bound, or returns a blocked/incomplete result, **the main agent takes over and continues immediately using its current model**. Report the reason briefly; do not ask the owner to choose a fallback or wait for quota to reset. Do not repeatedly retry the same blocked dispatch.

Before taking over assigned files, confirm the child is stopped and inspect any partial changes; preserve unrelated work. A timeout alone is not proof that the worker stopped. If its state is unresolved, use supported status/cancellation controls and continue independent work rather than racing it on the same files.

Do not silently substitute the direct DeepSeek API, a free endpoint, another paid provider, or another worker model. Do not enable Extra Usage, top up credits, alter privacy/region settings, or add credentials to keep a worker running. A missing registry/cap or denied permission causes fallback, not use-first/register-later. Normal safety and approval stops still apply to the main agent; fallback does not authorize irreversible actions.

## 4. Adoption and operating surface

- Add the policy pointer to the unit's existing `AGENTS.md`; preserve stricter unit rules and its risk tier. Medium/high work, other agents, and their configured models are unchanged.
- For OpenCode V2, copy the bundled profile into the unit at `.opencode/agents/execution-worker.md` only after checking for an existing same-named profile. Preserve local work and inspect conflicts instead of overwriting it. The kit's skill installer bundles the file; it does not install global OpenCode agents, change the primary agent, connect accounts, or configure billing.
- OpenCode reloads agent configuration automatically; `/reload` can force a reload. Verify the effective agent registration/model/permissions without making an inference request. Model inference needs the resource/data preflight above and is a separate measured check.
- Scope API inspection to the unit's `location[directory]` and verify the returned location; the server's default location need not be the shell's working directory. Report selected agent/model IDs and permission outcomes, not raw provider/request settings that may carry credentials.
- Other harnesses may use an already approved native child-session path that selects the exact Go model and enforces the same boundaries. Otherwise use main-agent fallback; this policy does not introduce a cross-CLI bridge or turn the optional Herdr protocol into a requirement.
- Record dispatch/fallback and the final verification in the existing task return. No separate ledger or new medium/high model-routing system is required.

## References

- [OpenCode V2 agents](https://opencode.ai/v2/docs/agents/)
- [OpenCode V2 permissions](https://opencode.ai/v2/docs/permissions/)
- [OpenCode Go models, allowance, privacy, and Extra Usage](https://opencode.ai/v2/docs/console/go/)

Catalog observation at adoption: `opencode-go/deepseek-v4.1-flash` advertises a `low` variant. This confirms a selectable reference, not a successful paid request, quota balance, or performance claim.
