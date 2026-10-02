# One Hit Kill Swordmaster: Setup And Lean Pilot

## Setup result

- Vault: `One Hit Kill Swordmaster/`
- Novel ID: `one-hit-kill-swordmaster`
- Source adapter: `wntl_markdown`
- Source: `https://wntl.net/series/ohks`
- Raw API: `https://wntl.net/api/chapters/ohks`
- Raw body: `https://wntl.net/content/ohks/{chapter}.md`
- Verified manifest: 95 published chapters
- Verified raw pool: `03_Raw/ch001-ch095`, no missing chapter IDs
- Raw text validation: English script and non-empty body for every fetched chapter
- Obsidian vault config copied from the working novel vault; production outputs
  were not created

The WNTL adapter and CLI persistence fix are in the shared pipeline. The CLI
previously printed `Fetched` without writing `source.json`; it now calls
`run_fetch_stage` and reports the persisted path.

## Experiment sample

Fixed seed: `20261003`

- In-sample: `ch001, ch004, ch014, ch019, ch037`
- Out-of-sample: `ch044, ch064, ch068, ch079, ch080`
- Sample source: fetched raw pool, not translated output
- Experiment vault: `04_Work/_experiments/v6_36_ohks_lean_v1/`

## Pilot result

The in-sample Lean run `v6-36-ohks-lean-is-v2` was stopped at QA. Literal and
chapter refinement completed for `ch001`, but the configured reasoning QA route
returned an empty assistant message with `finish_reason=length` and
`completion_tokens=4096` after `81.11s`. Metrics: 3 provider calls, 1 provider
failure, measured cost `$0.021512687`. No chapter was accepted, no OOS run was
started, and no production output or MoonRead content changed.

This is a valid provider-reliability failure observation, not a quality pass.
The requested 10-chapter translation test therefore remains incomplete until a
new authorized run addresses the provider block. The experiment deliberately
did not reroute providers or weaken QA.

## Recommendations

1. Keep the WNTL source pool and fixed sample manifest; they are ready for a
   resumed isolated run.
2. Probe the exact reasoning QA route with a bounded health check before paying
   for another multi-chapter run.
3. Do not promote Lean or publish pilot artifacts until the 10 selected
   chapters complete all stages, guardrails, Sentinel, and spot-check review.
4. Keep the normal 20-chapter Libra - Pilot Gate separate; this 10-chapter run
   is an experiment-only diagnostic requested for this novel.
