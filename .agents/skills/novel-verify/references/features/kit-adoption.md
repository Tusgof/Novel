# Kit adoption and agent policy

**What.** `.yuehua-kit.json` pins stable v4.0.5 at commit
`5af741b76e5c51442917d41af5ff91ec8ddc90bd`. `AGENTS.md` keeps UNIT/T2 and the
translation gates, and points to the pinned local browser/execution policies.
They remove a browser-vendor requirement and add low-reasoning execution only;
the main model, other agents and novel provider routes are unchanged.

**Drive it.** Set `YUEHUA_KIT_ROOT` to a temporary checkout of the verified release,
outside this repository. Resolve its tag to the lock's exact commit before use:
```
git -C "$env:YUEHUA_KIT_ROOT" rev-parse "v4.0.5^{commit}"
python "$env:YUEHUA_KIT_ROOT/tools/yuehua.py" doctor --format table .
python -m unittest test_kit_adoption test_opencode_provider test_workspace_routing test_xszj_adapter -v
```
Run `python test_translation.py` from `Deep Sea Embers/` and
`python -m unittest test_validate_herdr_envelope -v` from `scripts/` as usual.
The verified release checkout's yuehua-mode, start-unit, and yuehua-land
instructions are the procedure when installed skill provenance
predates the lock. `install-skills --dry-run` does not authorize a global install;
updating shared skills requires owner approval and a new session afterwards.

**Verify.** Policy/contract checks, prior-policy archive bytes, append-only
decisions, control hashes, and existing T2 tests pass from a clean clone. A fresh
agent session reads the current contract and both local policies. Inspect native
OpenCode registration at this unit's explicit location: `execution-worker` selects
Go DeepSeek V4.1 Flash `low`; shell, network/MCP, external paths, recursive
delegation and control-file editing are denied. Other profiles/defaults match
the baseline. Metadata checks do not require an inference request.

**Gotchas.**
- Read `policies/agent-browser.md` before browser work. Choose a suitable available tool without a vendor default; authority, credentials, vault, profiles, exposure, OAuth and observed-result boundaries still apply.
- Read `policies/execution-workers.md` before low-reasoning implementation. If resource/data permission, included quota/cap or safe native delegation cannot be confirmed, continue immediately with the current main model; inspect any stopped worker's partial work first. Do not ask for a fallback model or enable overage.
- The coding execution profile is separate from the existing higher-reasoning novel translation Worker and does not authorize pipeline calls, production writes or publication.
- Archives under `Backup_/policy/2026-11-05_pre-v4.0.5/` preserve history and are not active instructions. Product/runtime state stays out of this adoption change.
