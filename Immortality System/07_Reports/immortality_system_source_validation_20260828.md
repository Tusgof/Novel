# Immortality System Source Validation

Date: 2026-08-28

## Scope

- Novel: Immortality System
- Adapter: `novel543`
- Source: `https://www.novel543.com/0713488766/dir`
- Requested source range: `ch001-ch2570`

## Result

The complete requested source range is available locally after the bounded fetch completed.

| Check | Result |
|:--|:--|
| TOC manifest entries | 2,570 |
| Raw chapter files | 2,570 |
| Missing chapters | 0 |
| Empty bodies | 0 |
| Chapter-id mismatches | 0 |
| Empty titles | 0 |
| Source-script/replacement anomalies | 0 |
| Smallest body | 2,052 characters (`ch231`) |
| Largest body | 2,519 characters (`ch306`) |

## Recovery

The first full fetch reported `ch296` as suspected mojibake. Direct inspection showed the body was valid Traditional Chinese and contained only the kaomoji `胡土豆：٩(1^o^1)۶`, whose two `U+0E51` characters are Thai digit `1` code points.

The shared source validator was counting Thai digits as Thai prose. It now treats Thai digits as neutral numeric characters while continuing to reject Thai letters in Chinese source. A regression test covers this exact source pattern. `ch296` was refetched successfully after the validator fix.

## Provenance limitation

Novel543 is an aggregator/mirror. The Dek-D page identifies the Thai project, and Fanqie is the confirmed original/publication reference, but Novel543 remains the selected fetch source because its TOC exposes a contiguous range and its paginated extraction was verified. This is recorded as a provenance limitation, not silently treated as primary-source proof.

## Gate decision

The raw source pool is valid for Libra - Pilot Gate sampling. Sampling must use this verified raw pool, not translated output or MoonRead content.
