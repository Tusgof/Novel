# Governance and escaped defects

**Drive it (read-only, from the workspace root).**
```
python scripts/workspace_health.py check
python scripts/workspace_health.py status
python scripts/workspace_health.py reports --query dse-ch140-ch160
python scripts/workspace_health.py quality
python -m unittest test_governance test_semantic_detection -v
```

`--root <checkout>` observes a different checkout without changing it. Missing
local raw/output in a clone is unknown, not zero. Registry intent, checked-in
reader snapshot, observed local output, independent acceptance and live deployment
are distinct. Never expand the public registry to silence a local-only difference.

**Verify.** CI enforces line AND character budgets, reader-manifest/file identity,
evidenced incident cohorts and archive/decision preservation. Mutations for Chinese
term drift, mixed correct/rejected terms, the historical HGD leakage/voice cases,
and missing source must fail the real Sentinel/staging path. Clean-checkout tests
cover versioned code/policy/reader snapshots only, not ignored source/run evidence.

**Incident accounting.** Update `00_Config/quality_incidents.json` after a verified
public release and after a reader report. A new `verified-publication` cohort needs
novel, chapter ranges, timestamp, revision, live URL and a versioned evidence path.
An incident needs a stable ID, cohort, affected chapters, discovery date, detector,
and evidence. One report affecting many chapters is one incident. Generation or
unchanged republication adds no first-publication exposure. Historical snapshot
cohorts are explicitly not live probes; partial history never returns a precise
overall escape-rate claim. Preserve earlier records; later incidents can refer
to older publication cohorts. Review per cohort/time window before claiming a trend.

**Evidence lifecycle.** Old flat reports and dirty WIP retain their paths. The
derived index shows the newest timestamp per scope and the older-file count.
New machine reports are partitioned under ignored `07_Reports/generated/`; curate
only closure/regression evidence into Git. Nothing is auto-deleted or auto-pushed.

**Limits.** Source-backed checks are necessary but not general semantic evaluation.
Their green count does not measure omissions, speaker identity or every fact.
Retain QA and source reading; add a regression for each confirmed escape.
