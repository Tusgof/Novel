# MoonRead guest UX — paused at the owner's request

- **Goal:** Benchmark signed-out discovery, reading, accessibility, and return against comparable Thai and international fiction workflows. Do not change novel content or published ranges.
- **Saved state:** `moonread/reader-benchmark` at `9766787`. Local only; no push, merge, or deployment for this round.
- **Verified at `9766787`:** Chromium regressions 48/48, lint and smoke passed. The latest advisor also confirmed that opening an earlier bookmark within the same chapter no longer replaces the later reading position.
- **Release blocker:** The latest advisor returned NOT PASS. On fresh 375 × 600 touch emulation, open *เถ้าถ่านแห่งทะเลลึก* from Home. Before scrolling, tap the center of the story's contents or bookmarks tab. The fixed bottom navigation intercepts the tap; the contents tab can send the reader back to Home. The advisor also noted lower-priority desktop friction reaching Start Reading after opening the story by keyboard.
- **When authorized to resume:** Confirm the branch and reproduce the mobile issue with a coordinate tap before scrolling; locator-driven taps can scroll the tab clear. Fix and verify the current snapshot, obtain a fresh advisor PASS, then independent desktop and mobile reader results without friction, then exact-head GitHub CI before merge/deploy. Verify the merged SHA and live site afterward.
- **Not verified:** Latest release gates, physical iOS/Android, screen readers, and field performance. This pause applies only to the MoonRead UX task, not the Novel workspace as a whole.
