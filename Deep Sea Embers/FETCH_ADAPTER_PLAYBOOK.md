# Fetch Adapter Playbook

Use this playbook when an existing source site cannot be handled safely by the current adapter set.

Current baseline adapter:

- `novel_pipeline/adapters/piaotia.py`

This file is the reference implementation for:

- TOC discovery
- chapter content extraction
- GB-family decoding
- deterministic source validation

## Goal

Add or adapt fetch logic without breaking the adapter contract:

- `build_manifest()`
- `extract_content(html, encoding)`
- `fetch_chapter_text(meta)`

## Step 1: Inspect The Source Site

Before writing code, determine:

- TOC page URL
- chapter URL pattern
- whether links are static HTML or dynamic
- expected encoding
- likely body container
- obvious ad/nav/footer noise markers

Write down:

- one TOC URL
- one sample chapter URL
- one sample title
- one expected body paragraph

If you cannot identify these, do not write an adapter yet.

## Step 2: Decide Whether To Reuse Or Create

Choose one path:

1. Reuse an existing adapter as-is
2. Clone an existing adapter and change site rules
3. Create a new adapter file

Use `piaotia` as the default starting point when the source is:

- static HTML
- chapter-link driven
- simple enough for `urllib.request`

Do not add new network dependencies unless explicitly approved.

## Step 3: Implement TOC Discovery

The adapter must produce ordered `ChapterMeta` entries with:

- `index`
- `chapter_id`
- `title`
- `url`
- `source_id`

Checklist:

- dedupe duplicate chapter links
- normalize relative URLs
- preserve chapter order
- avoid nav/sidebar links
- ensure the first few entries are real chapter titles

Acceptance for this step:

- `fetch --adapter <name>` prints a sane manifest sample

## Step 4: Implement Content Extraction

The extraction path must be explicit and narrow.

Preferred pattern:

1. Primary content container rule
2. Fallback container rule
3. stop marker handling
4. nav/ad/footer stripping
5. paragraph flushing rules

Checklist:

- identify exact container ids/classes first
- if fallback mode is needed, activate it only after the title/body boundary
- split paragraphs on `<br>` and `<p>` intentionally
- strip nav text like previous/next chapter links
- stop on ad or footer markers when known

Acceptance for this step:

- the output body is non-empty
- body contains real prose, not page furniture

## Step 5: Handle Encoding

Encoding is adapter-specific.

Checklist:

- detect BOM if present
- inspect meta charset
- try only a small ordered set of candidate encodings
- reject replacement-character output
- validate the extracted script after decode

The `piaotia` baseline currently shows the right pattern:

- GB-family fallback
- charset probe from meta
- scoring decoded HTML
- mojibake rejection

Acceptance for this step:

- no `�`
- no obvious Thai/Latin corruption in Chinese source
- chapter text passes script validation

## Step 6: Register The Adapter

When a new adapter is needed:

1. create the adapter file in `novel_pipeline/adapters/`
2. register it in `novel_pipeline/adapters/__init__.py`
3. set the new project's `.system/config.yaml` `source.adapter`

Do not hide adapter selection inside unrelated pipeline code.

## Step 7: Run Deterministic Fetch Checks

At minimum, verify:

- manifest builds
- one sample chapter fetches
- one sample `03_Raw/<chapter>/source.json` exists
- no title/body swap
- no empty body
- no obvious HTML/nav/ad dump
- encoding is correct

Useful commands:

```powershell
novel-pipeline --config "<project>\\.system\\config.yaml" fetch --adapter "<adapter>"
novel-pipeline --config "<project>\\.system\\config.yaml" fetch --adapter "<adapter>" --chapter-id ch001
```

## Step 8: Decide If The Adapter Is Production-Ready

The adapter is ready only when:

- manifest order is correct
- chapter titles are correct
- extracted body is clean enough for block splitting
- encoding is stable on more than one chapter
- no site-specific noise remains that would poison glossary scan or translation

If any of these fail, do not proceed to batch fetch.

## Practical Notes From `piaotia`

Carry these lessons forward:

- exact container detection is better than generic HTML scraping
- fallback capture needs a clear start boundary
- stop markers are often site-specific and worth hard-coding narrowly
- HTML decode quality should be scored before content extraction is trusted
- source validation should fail early on mojibake, not after translation

## Stop Conditions

Stop and report if:

- the site is script-rendered and not fetchable with current tools
- encoding cannot be made deterministic
- chapter links are mixed with unrelated pages
- extraction returns ads/nav instead of prose
- sample chapters disagree about the body structure enough to invalidate the current approach

## Acceptance

An adapter change is accepted only when:

- the adapter contract is satisfied
- manifest generation works
- sample fetch works
- extracted text is clean enough for pipeline input
- deterministic validation passes before any translation work starts
