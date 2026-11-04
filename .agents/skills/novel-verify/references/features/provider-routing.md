# Provider and Worker routing

**What.** Each novel's `<Novel>/.system/providers.yaml` selects the Go model and explicit
`#variant` for each stage. `scripts/opencode_provider_shim.py` bridges native
OpenCode JSON into ProviderRunner. `.opencode/agents/novel-worker.md` selects the
execution Worker; `HERDR_WORKER_PROTOCOL.md` keeps its authority bounded.

**Drive it.** From the repository root:
```
opencode --version
python -m unittest test_opencode_provider test_workspace_routing test_xszj_adapter -v
python -m novel_pipeline.cli --config "<Novel>/.system/config.yaml" preflight
```
Run `python -m unittest test_validate_herdr_envelope -v` from `scripts/` and
`python test_translation.py` from `Deep Sea Embers/`.

**Verify.** All six configs select only the approved Go routes and variants;
the helper resolves to the root shared script; missing OpenCode blocks preflight;
truncated/empty/tool/error output is rejected; historical Luna envelopes still
validate. A provider-backed smoke uses invented text in an isolated fixture and
does not promote output. A real novel still needs its own source-backed quality
pilot, scoped guardrails/Sentinel and Inspector spot-check before publication.

**Gotchas.**
- OpenCode V2.2.5 is the measured CLI version. A provider-free preflight is not an auth/quota check. Connect Go with `/connect`; never read auth storage.
- Go cost=0 in native CLI output does not measure remaining allowance. Confirm allowance and Extra Usage before production; a $30 experiment or top-up needs separate approval.
- Changing provider/model/variant changes the Lean checkpoint dependency hash. Preserve old checkpoints and obtain a bounded rerun decision instead of rewriting their hashes.
- The shim uses native model limits and rejects a length-limited result; it does not shrink output budgets to get a call through.
