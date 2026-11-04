# OpenCode Go routing trial — 2026-11-05

## Scope and authority

The owner requested replacement of the previous model assignments with OpenCode
Go, then selected Claude Haiku 5.5 in place of the proposed Gemini route. The
Inspector role, Lean stages, novel-specific voice/glossary, and acceptance gates
are unchanged. This trial authorizes no production chapter continuation,
publication, $30 comparison experiment, credit top-up, or Extra Usage.

Implementation is on `opencode-go-routing`, based on `0243789`. The primary
checkout's pre-existing 14 modified files and 107 untracked files are protected.
Merge and merged-commit CI remain pending owner approval.

## Design and assignments

Reuse ProviderRunner and each novel's existing `providers.yaml`; model references
carry the exact native `#variant`, so no new routing schema is needed. Native
OpenCode CLI reads the prompt from stdin in an isolated temporary location using
a private server and a tool-denied text agent. A result is usable only after one
completed `stop` step. Empty/malformed/partial/tool/error output fails closed.

Haiku low handles literal translation and term extraction/harvest; Haiku medium
suggests term translations. DeepSeek high handles refinement and QA, with Haiku
high as their fallback. The other configured Go model is the only fallback for
term/literal work. Lean formatting remains local; fetch remains adapter-backed.
The bounded execution Worker defaults to DeepSeek high. Historical Luna envelopes
remain valid evidence, not a live fallback. See `NOVEL_OPERATOR_GUIDE.md` and
`HERDR_WORKER_PROTOCOL.md` for operation.

The routing choice is **inferred** to be a useful starting point from task shape,
not measured as the optimal quality/cost combination. Checkpoint input hashes
include provider configuration: old runs require a bounded rerun decision rather
than an automatic resume or forged cache hash.

## Measured transport evidence

- Native CLI: OpenCode `2.2.5`. Both requested Go model IDs and their chosen variants were present in the runtime catalog, and the existing Go integration had a credential connection. No credential value was inspected.
- A Haiku low invented-sentence probe returned `กัปตันเปิดประตู`.
- An early standalone DeepSeek QA probe received damaged Thai input from a PowerShell stdin fixture and correctly rejected it as question marks. This was test-input encoding damage, not translation evidence; the subsequent fixture was a UTF-8 file.
- A complete **invented two-paragraph fixture**, outside novel data, executed literal → refinement → QA → local format → term harvest through the real Lean stages and Go shim. It made four ProviderRunner calls with no failures and `28.530s` summed ProviderRunner duration, including native CLI startup. QA returned PASS with preserved dialogue/negation/entities. No production `05_Output` was created.
- Fixture output: `กัปตันเปิดประตูออก`, followed by `“อยู่ตรงนี้” เขาบอกกะลาสี เขาไม่ยิ้มเลย`.
- Seven native inference CLI invocations were made across the two small probes, four-stage fixture, and tool-denial probe below. The independent reviewer used separate authorized Go child-session inference. No full source chapter, provider comparison sweep, or publication ran.

Native CLI counters from the four-stage fixture:

| Stage | Input | Output | Reasoning | Cache read | Cache write |
| --- | ---: | ---: | ---: | ---: | ---: |
| Literal / Haiku low | 4 | 57 | 0 | 0 | 926 |
| Refine / DeepSeek high | 790 | 33 | 237 | 0 | 0 |
| QA / DeepSeek high | 766 | 22 | 174 | 0 | 0 |
| Harvest / Haiku low | 4 | 4 | 330 | 0 | 1149 |

These are native counters, not inferred billing totals. CLI reported cost zero;
Go allowance consumed and monetary cost are **not measured**. The usage-limit
endpoint returned no usable allowance data, so a production order must confirm
the remaining quota and Extra Usage boundary separately. The shim preserves raw
usage metadata and deliberately does not report subscription cost=0 as free usage.

## Verification and limits

Final measured checks:

- Root routing/adapter/Go tests: **32 passed**. The full DSE regression script passed independently after the doc/config changes. Worker-envelope tests: **11 passed**. Compile and `git diff --check` passed.
- Canonical SHA256 hashes in `DOC_RECOVERY.md`: all four match actual file bytes.
- Final Yuehua doctor: **0 failures**, with the unchanged 401-file historical portability warning and the expected unpushed-branch warning. Feature Map references pass.
- Native OpenCode resolved `novel-worker` to DeepSeek V4.1 Flash `high`. Runtime inspection accepted the text-agent config and its deny-all permissions. A native tool-request probe returned exactly `NO_TOOLS`, with one accepted `stop` step and zero tool events.
- A forced-timeout check against a private native OpenCode event stream (no inference) observed four owned processes, terminated the tree, and found **zero survivors**. This verifies the Windows lifecycle, not every platform's cancellation behavior.
- Primary-checkout status is still 14 modified / 107 untracked files on `main` at `0243789`. A pre-landing SHA256 baseline covers all 121 dirty files; no production or MoonRead change is part of this branch.

Independent Haiku-high review returned no blocking defect. The Inspector closed
its config/tool-denial and native-timeout evidence gaps with the probes above,
and added a positive preflight test. Its fallback-name concern is already covered
by `load_app_config` validation before preflight. The 120s scan/suggestion timeout
and 600s inner/660s outer provider defaults are distinct bounds, not a reason to
raise scan budgets. Native-token aggregation in the shared metrics summary stays
deferred: raw counters are retained and cost remains explicitly unmeasured.

Landing skips: push/PR CI, owner approval, merge, and merged-commit CI are pending;
no merge is self-approved. Production quality pilot and MoonRead publication are
out of this order. Rollback reference is the original base commit `0243789`;
restoring a route is a new reviewed change, never a reset of protected WIP.

The synthetic fixture demonstrates executable transport and stage wiring only.
It does not establish full-chapter quality, Chinese-source quality, long-output
limits, actual omission rates, novel voice quality, or the best model split.
Existing product content is unchanged; no MoonRead regeneration/build is required
for this code/config-only trial. Existing quality backlog stays outside scope.

## Sources and next check

- [OpenCode V2 models](https://opencode.ai/v2/docs/models): native model references and reasoning variants.
- [OpenCode V2 agents](https://opencode.ai/v2/docs/agents): model preference and ordered permissions.
- [OpenCode Go](https://opencode.ai/v2/docs/console/go): subscription limits, Extra Usage, and privacy.

After independent review and owner-approved landing, request one explicit source
chapter/range for a bounded quality pilot. Preserve existing checkpoints and WIP;
use the usual guardrails, blocking Sentinel, source-backed spot-check, and separate
MoonRead publication authority.
