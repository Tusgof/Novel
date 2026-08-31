# HERDR Worker Protocol

HERDR is the bounded handoff protocol for a coding-agent worker and an independent Inspector. It coordinates repository work; it does not change translation runtime behavior, provider routing, ledger state, or publication state.

## Actors and boundaries

- A HERDR worker is a coding agent running in a separate terminal tab or pane. Its declared runtime is `gpt-5.6-luna` with `reasoning=max`.
- Dashboard employee aliases (for example Ferryman, Quill, or Warden) are workflow labels, not HERDR worker identities, runtime permissions, or authorization sources.
- Translation provider stages (fetch, literal translation, refinement, QA, formatting, and their provider/model routes) are pipeline stages, not HERDR workers. HERDR must not invoke, reroute, or modify them.
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

- `status`: `complete` or `blocked`
- `local_hashes`: one or more labeled 40-character hexadecimal hashes
- `changed_paths`: paths changed by this worker only
- `commands`: exact command/result records
- `external_actions`: `{ "performed": boolean, "details": "..." }`
- `worktree`: `{ "dirty_wip_preserved": true, "diff_scope": [...] }`
- `blockers`, `manual_gates`, and `next_action`

The worker reports facts; the validator does not execute commands or infer provider/runtime state.

## Scope, concurrency, and stop rules

Never reset, clean, stage, commit, push, publish, delete, move, or overwrite the pre-existing dirty WIP. Do not edit a file concurrently with another worker. If a dirty path, ownership conflict, scope expansion, missing authority, credential request, provider/network/MCP request, external action, unexpected diff, or forbidden file need appears, stop immediately and report a blocked `RETURN`.

A timeout is not success: stop new work, preserve the last safe state, report the last completed command and blocker, and return `blocked`. Do not broaden scope or silently retry; the Inspector must issue a new `START` if work may resume.

## Independent verification

After `RETURN`, the Inspector independently checks the order/nonce, base and local hashes, exact allowed-scope diff, unchanged dirty-WIP paths, targeted test results, and the declared external-action truth. The Inspector also confirms no provider, network, credential, translation, publication, or deployment action occurred. A worker's self-report is not acceptance; unresolved manual gates remain blockers.
