# Research Profile Playbook

Use this when setting up `RESEARCH_PROFILE.yaml` for a new novel project.

1. Start with the two anchors:
   - `title`
   - `source_url`
2. Search the web using the title plus the source site. Prefer:
   - the source TOC/index page
   - publisher/aggregator synopsis pages
   - review or interview pages that discuss tone, pacing, and style
3. Fill only verified, durable fields:
   - `synopsis`: 2-4 sentences, no plot-spoilery detail beyond the core premise
   - `tags`: compact labels such as `nautical dark fantasy`, `mystery`, `supernatural horror`
   - `style_notes`: how the prose feels and what diction to avoid
   - `reader_expectations`: what a reader expects from tone, pacing, and reveal pattern
   - `review_summary`: consensus themes from reviews/interviews, not one reader's idiosyncratic take
   - `terminology`: durable names, titles, concepts, or setting phrases worth preserving
   - `reference_links`: the URLs you used so the profile can be audited later
4. Keep the file short. This is prompt context, not a wiki.
5. If a fact is uncertain, leave it out or put the uncertainty in `notes`.
6. Mark `status` as:
   - `pending` when the file is only scaffolded
   - `drafted` after the first research pass
   - `active` after Codex/user review
7. Revisit the file only when:
   - the source URL changes
   - a better synopsis or style discussion is found
   - later chapters prove an early assumption wrong
8. Do not build crawler logic into the pipeline just to fill this file. Record the verified operator result first, then let prompts consume that profile.
