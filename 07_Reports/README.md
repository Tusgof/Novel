# Evidence, not current state

Find the newest JSON/Markdown pair for a scope (older evidence is retained):

```powershell
python scripts/workspace_health.py reports --query dse-ch140-ch160
python scripts/workspace_health.py reports --query governance
```

The index is derived on demand, so there is no second inventory to maintain.
Historical flat files retain their original paths for citations. Nothing is
deleted or silently archived by this repair. New Sentinel machine runs go into
ignored `generated/<UTC month>/` with unique names; attach only an inspected
closure summary or selected regression evidence to a change. Local raw texts,
provider transcripts, browser data and credentials do not belong in public reports.

Use `status` for current state and `quality` for escaped defects. Checkpoint counts
and cost records in old reports are dated evidence, never current publication
intent, remaining quota, or proof of semantic fidelity.

Start here for this repair: `governance_detection_fix_20261115.md`.
