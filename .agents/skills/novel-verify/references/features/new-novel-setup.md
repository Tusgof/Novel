# Set up a new novel

**What.** Scaffold a new novel folder from an existing one, fetch raw source, prepare glossary, title sidecars, and the novel's voice, then run a small bounded Lean pilot before any production batch.

**How the owner asks.** "ช่วย setup นิยายใหม่ ชื่อ … ลิงก์ fetch …" — see `NOVEL_OPERATOR_GUIDE.md` §3.

**Drive it.**
```
python -m novel_pipeline.cli --config "<Existing Novel>/.system/config.yaml" init-novel --help
python -m novel_pipeline.cli --config "<New Novel>/.system/config.yaml" fetch --help
python -m novel_pipeline.cli --config "<New Novel>/.system/config.yaml" lean-run --chapters ch001-ch003 --run-id <id> --dry-run
```

**Verify.** The new folder has its own `<Novel>/.system/config.yaml`, `<Novel>/NOVEL_PROFILE.yaml`, and `<Novel>/.system/lean_voice.md`; raw chapters are present without sequence gaps; the pilot output passes the quality gates ([quality-gates.md](quality-gates.md)) and reads correctly against source.

**Gotchas.**
- A new novel does not inherit another novel's voice or glossary.
- Register the novel in `00_Config/novel_registry.json` only when it is ready to appear in MoonRead.
