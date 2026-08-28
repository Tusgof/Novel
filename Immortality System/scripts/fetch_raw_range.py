"""Fetch a verified raw chapter range without entering translation stages."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path(".system/config.yaml"))
    parser.add_argument("--start", type=int, required=True)
    parser.add_argument("--end", type=int, required=True)
    parser.add_argument("--force", action="store_true", help="Refetch existing source.json files.")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    if args.start < 1 or args.end < args.start:
        print("start/end must define a positive ascending range", file=sys.stderr)
        return 2

    from novel_pipeline.adapters import get_adapter
    from novel_pipeline.config import load_app_config
    from novel_pipeline.stages.fetch import (
        load_or_build_manifest,
        run_fetch_stage,
    )

    config = load_app_config(args.config)
    adapter = get_adapter(config.source)
    manifest = load_or_build_manifest(config=config, adapter=adapter, force=False)
    selected = [
        meta
        for meta in manifest
        if args.start <= int(meta.metadata.get("site_chapter", 0)) <= args.end
    ]
    expected = list(range(args.start, args.end + 1))
    selected_numbers = [int(meta.metadata["site_chapter"]) for meta in selected]
    missing_manifest = [number for number in expected if number not in selected_numbers]
    if missing_manifest:
        print(
            "manifest is missing requested source chapters: "
            + ", ".join(str(number) for number in missing_manifest[:20]),
            file=sys.stderr,
        )
        return 2

    fetched = 0
    skipped = 0
    failures: list[dict[str, str]] = []
    started = time.perf_counter()
    for position, meta in enumerate(selected, start=1):
        chapter_number = int(meta.metadata["site_chapter"])
        source_path = config.workspace.raw / meta.chapter_id / "source.json"
        if source_path.exists() and not args.force:
            try:
                payload = json.loads(source_path.read_text(encoding="utf-8"))
                if str(payload.get("chapter_id", "")) != meta.chapter_id or not str(
                    payload.get("raw_text", "")
                ).strip():
                    raise ValueError("existing source.json has missing chapter_id or raw_text")
                skipped += 1
                continue
            except (OSError, ValueError, json.JSONDecodeError) as exc:
                print(f"[{meta.chapter_id}] invalid cached source; refetching: {exc}")

        try:
            chapter = run_fetch_stage(
                config=config,
                chapter_id=meta.chapter_id,
                title=meta.title,
                adapter=adapter,
                chapter_meta=meta,
            )
            if not chapter.raw_text.strip():
                raise ValueError("adapter returned an empty body")
            fetched += 1
        except Exception as exc:  # noqa: BLE001 - preserve per-chapter evidence.
            failures.append({"chapter_id": meta.chapter_id, "error": str(exc)})
            print(f"[{meta.chapter_id}] FETCH_FAILED: {exc}", file=sys.stderr)
            continue

        if position == 1 or position % 25 == 0 or position == len(selected):
            elapsed = time.perf_counter() - started
            print(
                f"progress={position}/{len(selected)} chapter={chapter_number} "
                f"fetched={fetched} skipped={skipped} failures={len(failures)} "
                f"elapsed={elapsed:.1f}s",
                flush=True,
            )

    print(
        f"summary requested={len(expected)} fetched={fetched} skipped={skipped} "
        f"failures={len(failures)}",
        flush=True,
    )
    if failures:
        for failure in failures[:20]:
            print(f"failure {failure['chapter_id']}: {failure['error']}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
