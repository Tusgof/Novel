# HERDR Worker Protocol

HERDR is the bounded handoff protocol for Luna Max and an independent Inspector. It coordinates repository work and, when an explicit translation work order authorizes it, bounded execution of the existing translation pipeline. HERDR never grants authority by itself and does not change provider routing, quality gates, or publication state.

## Actors and boundaries

- Codex is the Inspector/Orchestrator and owns architecture, Layer 0 policy, work-order design, independent verification, acceptance, and publication decisions.
- A HERDR worker is Luna Max running in a separate terminal tab or pane. Its declared runtime is `gpt-5.6-luna` with `reasoning=max`.
- Dashboard employee aliases (for example Ferryman, Quill, or Warden) are workflow labels, not HERDR worker identities, runtime permissions, or authorization sources.
- Translation provider stages remain pipeline stages, not worker identities. A translation work order may authorize Luna to invoke existing pinned routes for an exact run/chapter range, but Luna must not reroute providers, weaken gates, force-accept QA, or alter publication state.
- The order is the authority. `allowed_paths` and `allowed_actions` are the complete write scope; `forbidden_*` entries and the dirty-WIP boundary remain in force.

## Preflight and transport

When the Inspector launches the worker through the agent tool, the launch arguments are literal:

```text
model = gpt-5.6-luna
reasoning_effort = max
surface = separate agent pane
```

Do not substitute `xhigh` for `max`. The agent tool creates the separate pane; do not use a manual right split.

1. Inspector sends an order with a unique `order_id`, `nonce`, repository, branch, and `base_hash`.
2. Worker confirms the identifiers and scope in `ACK`. Before an explicit smoke authorization, it does not read repository files, run commands, or edit.
3. If smoke is authorized, worker runs only the listed read-only checks in the current working directory and returns exact `cwd`, branch, `HEAD`, short status, and `edits=0` in `SMOKE`.
4. Worker uses a separate tab/pane and confirms that no other worker or operator is editing any file in its proposed scope. One active owner per file is required.
5. An explicit `START` authorization is required before any edit. Press Enter to acknowledge the handoff when the transport requires it.

The message order is:

```text
ACK -> SMOKE -> START -> RETURN
```

The validator checks one envelope at a time; Inspector verifies that the observed messages occurred in this order.

## Envelope shape

Every envelope is a JSON object with `protocol: "HERDR/1"`, a `phase` from `ACK`, `SMOKE`, `START`, or `RETURN`, the exact order identifiers, `repository`, `branch`, and a 40-character hexadecimal `base_hash`. It also contains:

```json
{
  "worker": {
    "kind": "coding-agent-worker",
    "surface": "separate-tab-pane",
    "runtime": "gpt-5.6-luna",
    "reasoning": "max",
    "sandbox": "workspace-write",
    "approval": "never"
  },
  "scope": {
    "allowed_paths": ["relative/path"],
    "allowed_actions": ["read", "edit"],
    "forbidden_paths": [],
    "forbidden_actions": ["network"],
    "dirty_wip_boundary": "exact pre-existing modified/untracked paths remain untouched"
  },
  "stop_conditions": ["unexpected scope expansion"],
  "handoff": {
    "transport": "Herdr",
    "recipient": "Inspector",
    "return_required": true,
    "worker_must_press_enter": true
  }
}
```

Paths are repository-relative exact paths. New files are listed by their file path. `ACK` additionally carries `ack: {"scope_echoed": true, "commands": 0, "files_read": 0, "edits": 0}`. `SMOKE` carries a `smoke` object with `cwd`, `branch`, `head`, exact `status`, and integer `edits: 0`. `START` carries `authorization: {"authorized": true}`. `RETURN` carries a `result` object with:

For a translation order, the envelope must additionally declare the exact `run_id`, chapter/block range, allowed pipeline commands and stages, pinned provider configuration, provider/network authority, spend boundary, required gates, and stop conditions. Credentials may be inherited from the approved environment but their values must never be read back, requested, printed, copied, or logged.

- `status`: `complete` or `blocked`
- `local_hashes`: one or more labeled 40-character hexadecimal hashes
- `changed_paths`: paths changed by this worker only
- `commands`: exact command/result records
- `external_actions`: `{ "performed": boolean, "details": "..." }`
- `worktree`: `{ "dirty_wip_preserved": true, "diff_scope": [...] }`
- `blockers`, `manual_gates`, and `next_action`

The worker reports facts; the validator does not execute commands or infer provider/runtime state.

## Scope, concurrency, and stop rules

Never reset, clean, stage, commit, push, publish, delete, move, or overwrite the pre-existing dirty WIP. Do not edit a file concurrently with another worker. If a dirty path, ownership conflict, scope expansion, missing authority, credential request, unauthorized provider/network/MCP request, external action outside the order, unexpected diff, or forbidden file need appears, stop immediately and report a blocked `RETURN`.

Routine recovery is allowed only when both the failure and recovery command are covered by the work order and an existing documented recovery path. A manual prompt, hard fail, exhausted provider route, source mismatch, proposed force-accept, gate reduction, routing change, or unfamiliar recurring failure is not routine: preserve evidence and return `blocked` to the Inspector.

A timeout is not success: stop new work, preserve the last safe state, report the last completed command and blocker, and return `blocked`. Do not broaden scope or silently retry; the Inspector must issue a new `START` if work may resume.

## Independent verification

After `RETURN`, the Inspector independently checks the order/nonce, base and local hashes, exact allowed-scope diff, unchanged dirty-WIP paths, targeted test results, ledger/artifact state, required quality gates, and the declared external-action truth. The Inspector confirms that provider, network, and translation actions stayed inside the explicit order and that no credential disclosure, publication, or deployment occurred. A worker's self-report is not acceptance; unresolved manual gates remain blockers.
