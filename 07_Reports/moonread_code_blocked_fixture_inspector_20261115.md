# MoonRead synthetic Code/blocked fixture — Inspector acceptance

Measured: reviewed the actual temporary fixture, test harness, result JSON and
desktop/mobile screenshots. The copied reader source matches the repository
byte-for-byte for all 38 declared files; all 984 protected real snapshot hashes
and the immutable Worker report hash match. No real book was enabled or generated.

The original one-off harness recorded browser errors without making them fail its
25-case result, and excluded all console text containing 404 indiscriminately.
Inspector retained that original evidence and ran a separate temporary harness
with strict page-error/external-request assertions, 404 exclusions restricted to
the four deliberately probed paths, a portable Node server launch and awaited
task-owned cleanup. It passed 26/26 checks, with zero unexpected console/page
errors or non-loopback requests and exactly four expected blocked-route 404s.
The original fixture, report and result were not overwritten.

Observed UI: Code/Lean/Pipe labels render on their intended chapters; blocked
rows are disabled and nonnavigable; unavailable direct routes return the intended
404; next/previous links skip blocked chapters; emphasis renders correctly; no
overflow at 1440/390/360/320. These are **synthetic** runtime checks, not translation
acceptance, real new-book rendering, deployed state or cross-browser coverage.

The fixture also confirms a payload-minimization backlog: book-detail HTML/RSC
serializes the blocked entries' raw `reason` and extra `error` probe although the
visible UI never displays them. The tested values are synthetic markers, and the
real generator's current reasons are validation codes, not credential material.
Do not claim the raw response omits those fields. No product change was made to
conceal this finding or to turn the observation into a passing privacy guarantee.

External evidence is under the task temp directory `moonread-code-blocked-01`:
the immutable Worker `result.json`/`harness.mjs`/`shots/`, plus Inspector
`result-inspector.json`/`inspector-harness.mjs`/`inspector-shots/`. No task-owned
server/browser remains. Real accepted-book scoped generation and fresh reader
gates remain separate and are still required before any release claim.
