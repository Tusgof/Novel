# MoonRead readiness — independent Inspector review

Scope: local reader readiness/bug fixes requested alongside two disjoint novel
Workers. No content generation, registry enablement, Git push, deployment or
public release is part of this acceptance. The user changed the lead's reasoning
setting; Worker models/routes, billing caps and quality gates remain unchanged.

## Measured

- Reviewed the audit/repair report hashes and actual store/consumer/dialog/search
  diff. Central `useSyncExternalStore` snapshots keep persisted state out of the
  SSR/first-hydration markup; mutations preserve the original storage schema.
- Independently ran lint, standalone Next production build (711 pages, workspace
  root warning gone), five generation regressions, five persisted-reader/browser
  regressions, and the existing desktop/mobile smoke. All passed.
- Inspected the actual mobile reader and desktop home screenshots outside the
  repository. Sampled smoke pages have no duplicate title, overflow, leaked
  emphasis or unexpected console error. The intentional 404 probe remains visible.
- Rechecked all 984 protected snapshot file hashes after the tests. Both new
  books remain reader-disabled; generator and generation-test WIP are untouched.

## Inspector additions after Worker return

- The new reader test suite logged console/page/external-request errors after its
  first test without a final failing assertion. Added a suite-wide assertion, so
  unexpected errors in **any** of the five cases fail acceptance; rerun passed.
- The new harness spawned `cmd.exe` unconditionally. It now starts Next through
  the current Node executable with portable paths, and awaits task-owned cleanup.
  Windows verified; Linux is not claimed from this environment.
- Smoke now reports the actual configured screenshot directory, rather than
  stale relative paths after `MOONREAD_SMOKE_OUTPUT_DIR` redirects its artifacts.
- Wired lint/build/reader regressions into existing CI after the declared npm
  install, with Playwright's declared Chromium installed in the ephemeral runner.
  Workflow syntax/step validation is local; no pushed/merged-SHA CI result exists.

## Limits / next gate

Local baseline reader repair is accepted, not landed or deployed. Stored dark
theme may still flash light before hydration. The later dedicated Code/blocked
synthetic fixture now passes independent strict browser checks; see
`moonread_code_blocked_fixture_inspector_20261115.md`. The baseline smoke's
default-true blocked flag is not itself evidence, and the one-off fixture is not
a new committed CI regression. Raw blocked reason fields remain serialized on
book-detail responses although the visible UI hides them; the finding is retained.
There are no Code-labeled chapters in this preserved six-book snapshot: Code
generation-label tests are fixture evidence only. Each accepted new book still
needs exact registry scope, protected scoped generation, new reader build/smoke,
owner-approved landing, merged-SHA CI and actual live verification.

Worker evidence: `moonread_readiness_audit_20261115.md` and
`moonread_readiness_repair_20261115.md`. Inspector screenshots are under the named
task temp directory `moonread-inspector-20261115`, not in the repository. Source
quality, translation acceptance and publication cohorts are separate checks.
