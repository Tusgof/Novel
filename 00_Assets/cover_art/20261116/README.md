# Two-book original cover art

Owner requested original covers based on the accepted first60 chapters before
merging the two-book reader release. These are illustrative interpretations,
not claims of canonical character portraits. No source cover or reference image
was supplied to the generator. Both plates have no baked-in text or branding.

## Generation provenance

- OpenAI Python SDK2.45.0, Responses API, existing local codex-lb connection.
- Mainline request/response model: `gpt-6.1-sol`.
- Requested `image_generation` tool model: `gpt-image-2`, high quality,
  `1024x1536`, PNG. One completed image call per cover, automatic SDK retries0.
- The Images endpoint had returned a backend-plan error. The owner explicitly
  selected the Responses-tool method instead. That method succeeded without any
  account, shared-skill, credential-store, service-config or billing-setting change.
- This service rejects optional `max_tool_calls`; the first trial stopped with400
  before generation. Removing only that parameter produced the successful images.
- Reported token usage is not a dollar bill or proof of remaining subscription quota.

## Assets and exact final prompts

| Novel | Original | Final prompt | Web derivative |
|:--|:--|:--|:--|
| Gacha | `a-gacha-addicts-fusionpunk-life-cover-v1.png` | `a-gacha-addicts-fusionpunk-life-prompt.txt` | `MoonRead/public/images/a-gacha-addicts-fusionpunk-life-cover.webp` |
| Investing | `investing-in-my-crippled-wife-cover-v1.png` | `investing-in-my-crippled-wife-prompt.txt` | `MoonRead/public/images/investing-in-my-crippled-wife-cover.webp` |

Derivative paths are repository-relative. WebP plates are768x1152, preserving the
full2:3 composition with no crop, Pillow LANCZOS resize, quality86, method6.

Original PNG SHA256:

- Gacha: `af1dcf71d3e4c0c36f498ae6dc6ef009871dae36d39a29e26d68d9365a5ddf89`
- Investing: `d9056d93fab08ceabb5e3379bff0db8a4e5cb3e700416a353411b9738c6c23bc`

## Visual acceptance and handoff

- Gacha: one defiant adult silhouette, one plain gold coin, black fire, wet
  industrial/occult city, charcoal/gold/petrol palette and quiet upper title space.
- Investing: brown-haired adult husband, black-haired/blue-eyed adult wife visibly
  in a wheelchair, voluntary hand contact, restrained gold/frost bond and hopeful
  home light. No instant cure, hospital/pity framing or sexualization.
- Both inspected at full size for faces/hands, crop, focal hierarchy, accidental
  writing, watermarks and distracting generation artifacts; no correction needed.
- Keep typography separate. Existing MoonRead cover components use the web assets
  directly; no renderer/style change is required. Leave the upper space available
  for a future separately approved typographic treatment.
