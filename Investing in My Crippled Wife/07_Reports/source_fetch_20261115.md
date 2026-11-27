# Source fetch — 2026-11-15

## Goal and check

Fill `03_Raw` for `investing-in-my-crippled-wife` from the owner-selected listing
`https://toonnovel.com/novel/investing-in-my-crippled-wife-every-return-makes-me-stronger/`,
without translating, calling a provider, generating reader content or publishing.
Done means every catalogued chapter is present locally, readable, and numbered
without gaps or mismatched titles.

## How

- The shared adapter registry had no adapter for this site, so a fetch would have
  failed with `Unknown fetch adapter`. Added `novel_pipeline/adapters/toonnovel.py`
  (catalog from the server-rendered chapter list, filtered by series slug; body
  from `div#content` with per-paragraph comment buttons, svg icons and scripts
  dropped) plus six hermetic tests and CI wiring.
- `source.adapter: toonnovel` and the listing URL are pinned in `.system/config.yaml`
  and `NOVEL_PROFILE.yaml`; the adapter is never inherited from another novel.
- Fetched with this novel's explicit `--config`; the corpus stays in the ignored
  `03_Raw/`.

## Measured

- 249 chapter directories `ch001`-`ch249`, no numbering gaps.
- Body length: min 5,572 / max 10,134 / mean 6,735 characters; none under 1,000.
- Every chapter has a title, the title number matches its chapter ID, no Han text,
  and every `source_url` points at the selected listing.
- All 249 chapters are publicly readable on that site; `chapter/250` returns 404,
  so the catalog end is confirmed. No login, coin spend, paywall bypass or mirror
  was used.

## Not claimed

- No translation, glossary approval, Thai title sidecar, pilot or publication.
  The reader entry stays disabled and no registry range changed.
- A fetched corpus is local evidence only; it is not a reproducible clean-checkout
  artifact, a translation licence or an approved term list.
- The adapter is a PR (`adapter/toonnovel`), not merged code; merge and any later
  pilot need separate owner decisions and current Go allowance verification.

## Next gates

1. Thai title sidecars under `04_Work/chXXX/title.json`.
2. Chapter-backed glossary proposals and human approval.
3. Bounded Lean pilot, then QA/guardrails/Sentinel and Inspector source reading.
