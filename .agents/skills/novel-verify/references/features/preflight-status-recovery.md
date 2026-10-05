# Preflight, status, and recovery

**What.** Read-only readiness checks, run status, resuming interrupted runs, and verification reports.

**Drive it.**
```
python -m novel_pipeline.cli --config "<Novel>/.system/config.yaml" preflight
python -m novel_pipeline.cli --config "<Novel>/.system/config.yaml" status --run-id <id>
python -m novel_pipeline.cli --config "<Novel>/.system/config.yaml" resume --run-id <id> --manual-action-mode stop
python -m novel_pipeline.cli --config "<Novel>/.system/config.yaml" report recovery-drill
python -m novel_pipeline.cli --config "<Novel>/.system/config.yaml" report provider-usage --help
```

**Verify.** `preflight` lists every provider as `ready` and shows no **Blocking** item; `report recovery-drill` is `accepted`.

**Gotchas.**
- Provider configs name commands, not machine paths; on Windows the loader resolves npm `.cmd` shims through PATH. If a provider shows as missing, fix PATH rather than writing an absolute path into a config.
- A dirty working tree is a warning in `preflight`; commit or stash before large write actions.
- Recovery procedures and their history are in `DOC_RECOVERY.md`.
- Tests: `python -m unittest test_workspace_routing test_xszj_adapter` at the root and `python test_translation.py` inside `Deep Sea Embers` (set `PYTHONUTF8=1` on Windows consoles).
