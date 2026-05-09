from __future__ import annotations

import argparse
import sys
from pathlib import Path

from novel_pipeline.config import load_app_config
from novel_pipeline.logging import configure_logging
from novel_pipeline.operator_ui import serve_operator_ui
from novel_pipeline.preflight import build_preflight_summary, print_preflight_summary
from novel_pipeline.project_setup import initialize_novel_project
from novel_pipeline.reports import (
    build_checkpoint_report,
    build_cleanliness_report,
    build_preflight_report,
    build_recovery_drill_report,
    build_product_review_report,
    build_glossary_audit_report,
    build_glossary_conflicts_report,
    build_glossary_decisions_report,
    build_glossary_guard_report,
    build_provider_usage_report,
)
from novel_pipeline.pipeline import (
    approve_terms_command,
    ManualActionRequired,
    format_command,
    inspect_block_command,
    qa_command,
    refine_command,
    rerun_block_pipeline,
    resume_pipeline,
    run_batch_pipeline,
    run_pipeline,
    scan_terms_command,
    status_run,
    translate_literal_command,
)

def _warn_research_readiness(config, *, bounded: bool) -> int:
    try:
        summary = config.ensure_translation_ready(bounded=bounded)
    except ValueError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1
    if summary["readiness"] == "degraded":
        warnings = "; ".join(summary["warnings"]) or "bounded translation only"
        print(f"[WARN] Research profile is drafted. {warnings}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="novel-pipeline",
        description="CLI for the novel translation pipeline.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(".system/config.yaml"),
        help="Path to the main config file.",
    )
    parser.add_argument(
        "--novel",
        default=None,
        help="Novel ID override.",
    )
    parser.add_argument(
        "--run-id",
        default=None,
        help="Explicit run ID for resume or status.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-run of already-committed stages.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # run command
    run_parser = subparsers.add_parser("run", help="Run a full end-to-end pipeline for one chapter.")
    run_parser.add_argument("--input-file", type=Path, default=None, help="Path to source chapter file.")
    run_parser.add_argument("--text", default=None, help="Raw source text to translate (pasted).")
    run_parser.add_argument("--title", default="", help="Chapter title.")
    run_parser.add_argument("--chapter-id", default=None, help="Chapter ID. Defaults to novel ID if not set.")
    run_parser.add_argument("--run-id", default=argparse.SUPPRESS, help="Explicit run ID.")
    run_parser.add_argument("--force", action="store_true", default=argparse.SUPPRESS, help="Force re-run of already-committed stages.")
    run_parser.add_argument("--style-profile", default=None, help="Style profile key to use.")
    run_parser.add_argument("--range", dest="chapter_range", default="", help="Chapter range for batch mode (e.g. 'ch001-ch010' or 'ch001,ch003,ch007').")
    run_parser.add_argument("--stop-after", choices=["glossary-scan"], help="Stop after the specified stage (currently only 'glossary-scan' supported).")
    run_parser.add_argument("--adapter", default="", help="Fetch adapter name (e.g. 'piaotia'). Overrides config.")

    # resume command
    resume_p = subparsers.add_parser("resume", help="Resume a previously interrupted run.")
    resume_p.add_argument("--run-id", default=argparse.SUPPRESS, help="Run ID to resume.")
    resume_p.add_argument("--force", action="store_true", default=argparse.SUPPRESS, help="Force re-run of already-committed block stages.")
    resume_p.add_argument("--style-profile", default=None, help="Style profile key to use.")
    resume_p.add_argument("--until-chapter", default=None, help="Resume only until and including this chapter ID.")
    resume_p.add_argument("--until-block", default=None, help="Resume only until and including this block ID.")
    resume_p.add_argument(
        "--manual-action-mode",
        choices=["interactive", "stop"],
        default="interactive",
        help="How to handle manual prompts during resume.",
    )

    # status command
    status_p = subparsers.add_parser("status", help="Show status of runs.")
    status_p.add_argument("--run-id", default=argparse.SUPPRESS, help="Run ID to inspect.")

    # report command family
    report_p = subparsers.add_parser("report", help="Generate verification reports.")
    report_subparsers = report_p.add_subparsers(dest="report_command", required=True)

    report_checkpoint_p = report_subparsers.add_parser("checkpoint", help="Generate a checkpoint report for a run.")
    report_checkpoint_p.add_argument("--run-id", required=True, help="Run ID to summarize.")
    report_checkpoint_p.add_argument("--output", type=Path, default=None, help="Output markdown path.")

    report_cleanliness_p = report_subparsers.add_parser("cleanliness", help="Generate a final-output cleanliness report.")
    report_cleanliness_p.add_argument("--run-id", required=True, help="Run ID to inspect.")
    report_cleanliness_p.add_argument(
        "--chapter-id",
        action="append",
        default=[],
        help="Chapter ID to inspect. May be repeated.",
    )
    report_cleanliness_p.add_argument("--output", type=Path, default=None, help="Output markdown path.")

    report_provider_p = report_subparsers.add_parser("provider-usage", help="Generate a provider usage/failure report.")
    report_provider_p.add_argument("--run-id", required=True, help="Run ID to inspect.")
    report_provider_p.add_argument("--output", type=Path, default=None, help="Output markdown path.")

    report_glossary_p = report_subparsers.add_parser("glossary-decisions", help="Generate a glossary decisions report from glossary_approved records.")
    report_glossary_p.add_argument("--run-id", required=True, help="Run ID to inspect.")
    report_glossary_p.add_argument("--output", type=Path, default=None, help="Output markdown path.")

    report_conflicts_p = report_subparsers.add_parser("glossary-conflicts", help="Generate a glossary conflicts report from glossary notes and scan artifacts.")
    report_conflicts_p.add_argument("--run-id", default=None, help="Optional batch run ID to inspect for scan candidates.")
    report_conflicts_p.add_argument("--output", type=Path, default=None, help="Output markdown path.")

    report_audit_p = report_subparsers.add_parser("glossary-audit", help="Generate a chapter audit report from source blocks and final outputs.")
    report_audit_p.add_argument("--run-id", required=True, help="Run ID to inspect.")
    report_audit_p.add_argument("--output", type=Path, default=None, help="Output markdown path.")

    report_guard_p = report_subparsers.add_parser("glossary-guard", help="Generate a glossary guard verification report from source blocks.")
    report_guard_p.add_argument("--run-id", required=True, help="Run ID to inspect.")
    report_guard_p.add_argument("--output", type=Path, default=None, help="Output markdown path.")

    report_preflight_p = report_subparsers.add_parser("preflight", help="Generate a preflight diagnostics report for the current workspace.")
    report_preflight_p.add_argument("--output", type=Path, default=None, help="Output markdown path.")

    report_recovery_p = report_subparsers.add_parser("recovery-drill", help="Generate a recovery-readiness report for canonical docs and git guardrails.")
    report_recovery_p.add_argument("--output", type=Path, default=None, help="Output markdown path.")

    report_product_p = report_subparsers.add_parser("product-review", help="Generate a product-complete review report for a run.")
    report_product_p.add_argument("--run-id", required=True, help="Run ID to inspect.")
    report_product_p.add_argument("--output", type=Path, default=None, help="Output markdown path.")

    # inspect-block command
    inspect_p = subparsers.add_parser("inspect-block", help="Inspect one block without modifying artifacts.")
    inspect_p.add_argument("--run-id", required=True, help="Run ID that owns the block artifacts.")
    inspect_p.add_argument("--block-id", required=True, help="Block ID to inspect, e.g. ch001-block-004.")

    operator_p = subparsers.add_parser("operator", help="Start the local operator window.")
    operator_p.add_argument("--run-id", default=argparse.SUPPRESS, help="Optional run ID to load on startup.")
    operator_p.add_argument("--host", default="127.0.0.1", help="Host to bind the operator window server.")
    operator_p.add_argument("--port", type=int, default=8765, help="Port to bind the operator window server.")
    operator_p.add_argument("--open-browser", action="store_true", default=False, help="Open the operator window in a browser.")

    preflight_p = subparsers.add_parser("preflight", help="Run environment, config, and git guardrail checks.")
    preflight_p.add_argument("--json", action="store_true", default=False, help="Print the preflight summary as JSON.")

    init_novel_p = subparsers.add_parser("init-novel", help="Scaffold a new novel project from the current workspace.")
    init_novel_p.add_argument("--project-root", type=Path, required=True, help="Target directory for the new novel project.")
    init_novel_p.add_argument("--title", required=True, help="Primary novel title.")
    init_novel_p.add_argument("--source-url", required=True, help="Primary source TOC/index URL used for fetch.")
    init_novel_p.add_argument("--novel-id", default="", help="Novel ID override. Defaults to a slug from title.")
    init_novel_p.add_argument("--alias", action="append", default=[], help="Alternate title. May be repeated.")
    init_novel_p.add_argument("--source-language", default="zh", help="Source language code.")
    init_novel_p.add_argument("--target-language", default="th", help="Target language code.")
    init_novel_p.add_argument("--genre", default="", help="Initial genre label.")
    init_novel_p.add_argument("--adapter", default="", help="Fetch adapter name. Defaults to the current config adapter.")
    init_novel_p.add_argument("--style-profile", default="", help="Default style profile key. Defaults to current config.")

    # rerun-block command
    rerun_p = subparsers.add_parser("rerun-block", help="Rerun one block from a selected stage.")
    rerun_p.add_argument("--run-id", required=True, default=argparse.SUPPRESS, help="Run ID that owns the block artifacts.")
    rerun_p.add_argument("--block-id", required=True, help="Block ID to rerun, e.g. ch001-block-004.")
    rerun_p.add_argument(
        "--from-stage",
        required=True,
        choices=["literal", "translate", "translating", "refine", "refining", "qa", "format", "formatting"],
        help="Stage to rerun from. Upstream artifacts are reused.",
    )
    rerun_p.add_argument("--style-profile", default=None, help="Style profile key to use.")

    # fetch command (stub)
    fetch_p = subparsers.add_parser("fetch", help="Fetch a chapter from a website adapter or local file.")
    fetch_p.add_argument("--adapter", default="", help="Fetch adapter name (e.g. 'piaotia').")
    fetch_p.add_argument("--toc-url", default="", help="TOC URL (overrides config).")
    fetch_p.add_argument("--input-file", type=Path, default=None, help="Path to source file.")
    fetch_p.add_argument("--chapter-id", default=None, help="Chapter ID.")

    # scan-terms command (stub)
    scan_p = subparsers.add_parser("scan-terms", help="Scan candidate terms from a chapter.")
    scan_p.add_argument("--chapter-id", required=True, help="Chapter ID.")
    scan_p.add_argument("--run-id", default=argparse.SUPPRESS, help="Optional run ID for ledger commit.")
    scan_p.add_argument("--force", action="store_true", default=argparse.SUPPRESS, help="Rescan even if ledger stage exists.")

    # approve-terms command (stub)
    approve_p = subparsers.add_parser("approve-terms", help="Interactively approve pending terms.")
    approve_p.add_argument("--chapter-id", required=True, help="Chapter ID.")
    approve_p.add_argument("--run-id", default=argparse.SUPPRESS, help="Optional run ID for ledger commit.")
    approve_p.add_argument("--force", action="store_true", default=argparse.SUPPRESS, help="Re-check approval queue even if committed.")

    # translate-literal command (stub)
    trans_p = subparsers.add_parser("translate-literal", help="Run literal translation for one block.")
    trans_p.add_argument("--chapter-id", required=True, help="Chapter ID.")
    trans_p.add_argument("--block-id", required=True, help="Block ID.")
    trans_p.add_argument("--run-id", default=argparse.SUPPRESS, help="Optional run ID for ledger commit.")
    trans_p.add_argument("--force", action="store_true", default=argparse.SUPPRESS, help="Rerun even if committed.")

    # refine command (stub)
    refine_p = subparsers.add_parser("refine", help="Refine a literal draft.")
    refine_p.add_argument("--chapter-id", required=True, help="Chapter ID.")
    refine_p.add_argument("--block-id", required=True, help="Block ID.")
    refine_p.add_argument("--run-id", default=argparse.SUPPRESS, help="Optional run ID for ledger commit.")
    refine_p.add_argument("--force", action="store_true", default=argparse.SUPPRESS, help="Rerun even if committed.")
    refine_p.add_argument("--style-profile", default=None, help="Style profile key to use.")

    # qa command (stub)
    qa_p = subparsers.add_parser("qa", help="Run QA gate on a refined draft.")
    qa_p.add_argument("--chapter-id", required=True, help="Chapter ID.")
    qa_p.add_argument("--block-id", required=True, help="Block ID.")
    qa_p.add_argument("--run-id", default=argparse.SUPPRESS, help="Optional run ID for ledger commit.")
    qa_p.add_argument("--style-profile", default=None, help="Style profile key to use.")

    # format command (stub)
    fmt_p = subparsers.add_parser("format", help="Format a QA-passed block.")
    fmt_p.add_argument("--chapter-id", required=True, help="Chapter ID.")
    fmt_p.add_argument("--block-id", required=True, help="Block ID.")
    fmt_p.add_argument("--run-id", default=argparse.SUPPRESS, help="Optional run ID for ledger commit.")
    fmt_p.add_argument("--force", action="store_true", default=argparse.SUPPRESS, help="Rerun even if committed.")

    return parser


def cmd_run(args: argparse.Namespace, config) -> int:
    chapter_id = args.chapter_id or config.novel_id
    
    # Override adapter if provided
    if args.adapter:
        config.source.adapter = args.adapter
    
    # Batch mode
    if args.stop_after and not args.chapter_range:
        print("[ERROR] --stop-after is currently supported only for batch --range runs.", file=sys.stderr)
        return 1
    if args.chapter_range:
        if not args.stop_after:
            readiness_result = _warn_research_readiness(config, bounded=True)
            if readiness_result:
                return readiness_result
        from novel_pipeline.text_utils import parse_chapter_range
        try:
            chapter_ids = parse_chapter_range(args.chapter_range)
        except ValueError as exc:
            print(f"[ERROR] {exc}", file=sys.stderr)
            return 1
        if not chapter_ids:
            print("[ERROR] No chapters parsed from --range", file=sys.stderr)
            return 1
        print(f"[BATCH] Chapters: {', '.join(chapter_ids)}")
        try:
            results = run_batch_pipeline(
                config=config,
                chapter_ids=chapter_ids,
                style_profile=args.style_profile,
                run_id=args.run_id,
                force=args.force,
                stop_after=args.stop_after,
            )
            if args.stop_after == "glossary-scan":
                print(f"[BATCH] Stopped after glossary scan. Review batch glossary artifact before approval.")
                print(f"[BATCH] Run status: novel-pipeline --config '{args.config}' status --run-id {args.run_id}")
                print(f"[BATCH] To resume with approval: novel-pipeline --config '{args.config}' resume --run-id {args.run_id}")
            else:
                completed_ids = [ctx.chapter_source.chapter_id if ctx.chapter_source else "?" for ctx in results]
                print(f"[BATCH] Run complete. {len(completed_ids)} chapters processed: {', '.join(completed_ids)}")
            return 0
        except Exception as exc:
            print(f"[ERROR] Batch run failed: {exc}", file=sys.stderr)
            return 1
    
    # Single chapter mode (existing code)
    readiness_result = _warn_research_readiness(config, bounded=True)
    if readiness_result:
        return readiness_result
    try:
        ctx = run_pipeline(
            config=config,
            chapter_id=chapter_id,
            title=args.title,
            input_file=args.input_file,
            text=args.text,
            style_profile=args.style_profile,
            run_id=args.run_id,
            force=args.force,
            adapter_name=args.adapter,
        )
        print(f"[{ctx.run_id}] Run complete. Output written to {ctx.config.workspace.output}")
        return 0
    except Exception as exc:
        print(f"[ERROR] Run failed: {exc}", file=sys.stderr)
        return 1


def cmd_resume(args: argparse.Namespace, config) -> int:
    run_id = args.run_id
    if run_id is None:
        # Try to find the latest run_id from ledger
        ledger_path = config.ledger_path
        if not ledger_path.exists():
            print("No ledger file found. Nothing to resume.", file=sys.stderr)
            return 1
        # Read last line of ledger to get latest run_id
        lines = ledger_path.read_text(encoding="utf-8").strip().splitlines()
        if not lines:
            print("Ledger file is empty. Nothing to resume.", file=sys.stderr)
            return 1
        import json
        last_record = json.loads(lines[-1])
        run_id = last_record.get("run_id", "")
        if not run_id:
            print("Cannot determine run_id from ledger.", file=sys.stderr)
            return 1
        print(f"Using latest run_id: {run_id}")

    readiness_result = _warn_research_readiness(
        config,
        bounded=bool(getattr(args, "until_chapter", None) or getattr(args, "until_block", None)),
    )
    if readiness_result:
        return readiness_result

    try:
        ctx = resume_pipeline(
            config=config,
            run_id=run_id,
            force=args.force,
            manual_action_mode=getattr(args, "manual_action_mode", "interactive"),
            until_chapter=getattr(args, "until_chapter", None),
            until_block=getattr(args, "until_block", None),
        )
        print(f"[{ctx.run_id}] Resume complete.")
        return 0
    except ManualActionRequired as exc:
        print(f"[MANUAL ACTION REQUIRED] {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"[ERROR] Resume failed: {exc}", file=sys.stderr)
        return 1


def cmd_status(args: argparse.Namespace, config) -> int:
    result = status_run(config=config, run_id=args.run_id)
    return 0


def cmd_report(args: argparse.Namespace, config) -> int:
    if args.report_command == "checkpoint":
        result = build_checkpoint_report(config=config, run_id=args.run_id, output=args.output)
    elif args.report_command == "cleanliness":
        result = build_cleanliness_report(
            config=config,
            run_id=args.run_id,
            chapter_ids=args.chapter_id or None,
            output=args.output,
        )
    elif args.report_command == "provider-usage":
        result = build_provider_usage_report(config=config, run_id=args.run_id, output=args.output)
    elif args.report_command == "glossary-decisions":
        result = build_glossary_decisions_report(config=config, run_id=args.run_id, output=args.output)
    elif args.report_command == "glossary-conflicts":
        result = build_glossary_conflicts_report(config=config, run_id=args.run_id, output=args.output)
    elif args.report_command == "glossary-audit":
        result = build_glossary_audit_report(config=config, run_id=args.run_id, output=args.output)
    elif args.report_command == "glossary-guard":
        result = build_glossary_guard_report(config=config, run_id=args.run_id, output=args.output)
    elif args.report_command == "preflight":
        result = build_preflight_report(config=config, output=args.output)
    elif args.report_command == "recovery-drill":
        result = build_recovery_drill_report(config=config, output=args.output)
    elif args.report_command == "product-review":
        result = build_product_review_report(config=config, run_id=args.run_id, output=args.output)
    else:
        print(f"[ERROR] Unknown report command: {args.report_command}", file=sys.stderr)
        return 1

    print(str(result["path"]))
    return 1 if result.get("actionable_failure") else 0


def cmd_inspect_block(args: argparse.Namespace, config) -> int:
    try:
        inspect_block_command(config=config, run_id=args.run_id, block_id=args.block_id)
        return 0
    except Exception as exc:
        print(f"[ERROR] inspect-block failed: {exc}", file=sys.stderr)
        return 1


def cmd_operator(args: argparse.Namespace, config) -> int:
    try:
        server = serve_operator_ui(
            config=config,
            host=args.host,
            port=args.port,
            run_id=getattr(args, "run_id", None),
            open_browser=args.open_browser,
        )
    except Exception as exc:
        print(f"[ERROR] operator failed to start: {exc}", file=sys.stderr)
        return 1

    url = f"http://{args.host}:{args.port}/"
    print(f"[operator] Serving local operator window at {url}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("[operator] Stopped.")
    finally:
        server.server_close()
    return 0


def cmd_preflight(args: argparse.Namespace, config) -> int:
    summary = build_preflight_summary(config)
    if args.json:
        import json
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print_preflight_summary(summary)
    return 1 if summary.get("blocking_reasons") else 0


def cmd_init_novel(args: argparse.Namespace, config) -> int:
    try:
        result = initialize_novel_project(
            template_config=config,
            project_root=args.project_root,
            title=args.title,
            source_url=args.source_url,
            novel_id=args.novel_id or None,
            aliases=args.alias,
            source_language=args.source_language,
            target_language=args.target_language,
            genre=args.genre,
            adapter=args.adapter,
            style_profile=args.style_profile,
        )
    except Exception as exc:
        print(f"[ERROR] init-novel failed: {exc}", file=sys.stderr)
        return 1

    print(f"project_root: {result['project_root']}")
    print(f"config_path: {result['config_path']}")
    print(f"profile_path: {result['profile_path']}")
    if "research_profile_path" in result:
        print(f"research_profile_path: {result['research_profile_path']}")
    return 0


def cmd_rerun_block(args: argparse.Namespace, config) -> int:
    if not args.run_id:
        print("[ERROR] rerun-block requires --run-id.", file=sys.stderr)
        return 1
    readiness_result = _warn_research_readiness(config, bounded=True)
    if readiness_result:
        return readiness_result
    try:
        rerun_block_pipeline(
            config=config,
            run_id=args.run_id,
            block_id=args.block_id,
            from_stage=args.from_stage,
            style_profile=args.style_profile,
        )
        return 0
    except Exception as exc:
        print(f"[ERROR] rerun-block failed: {exc}", file=sys.stderr)
        return 1


def cmd_fetch(args: argparse.Namespace, config) -> int:
    if args.adapter:
        config.source.adapter = args.adapter
    if args.toc_url:
        config.source.toc_url = args.toc_url

    if config.source.adapter:
        from novel_pipeline.adapters import get_adapter
        from novel_pipeline.stages.fetch import load_or_build_manifest, resolve_chapter_meta, run_fetch_stage
        adapter = get_adapter(config.source)
        manifest = load_or_build_manifest(config=config, adapter=adapter, force=False)

        if not args.chapter_id:
            # Just print manifest
            print(f"Found {len(manifest)} chapters:")
            for m in manifest[:10]:
                print(f"  {m.chapter_id}: {m.title}")
            if len(manifest) > 10:
                print(f"  ... and {len(manifest) - 10} more")
            return 0

        chapter_meta = resolve_chapter_meta(manifest, args.chapter_id)
        print(f"Fetching: {chapter_meta.title} ({chapter_meta.url})")
        text = adapter.fetch_chapter_text(chapter_meta)
        print(f"Fetched {len(text)} chars")
        return 0

    if args.input_file:
        from novel_pipeline.stages.fetch import run_fetch_stage
        chapter_id = args.chapter_id or "local"
        cs = run_fetch_stage(
            config=config,
            chapter_id=chapter_id,
            title="",
            input_file=args.input_file,
        )
        print(f"[fetch] Loaded {len(cs.raw_text)} chars from {args.input_file}")
        return 0

    print("[fetch] Provide --adapter or --input-file.")
    return 1


def cmd_scan_terms(args: argparse.Namespace, config) -> int:
    try:
        scan_terms_command(
            config=config,
            chapter_id=args.chapter_id,
            run_id=getattr(args, "run_id", None),
            force=getattr(args, "force", False),
        )
        return 0
    except Exception as exc:
        print(f"[ERROR] scan-terms failed: {exc}", file=sys.stderr)
        return 1


def cmd_approve_terms(args: argparse.Namespace, config) -> int:
    try:
        approve_terms_command(
            config=config,
            chapter_id=args.chapter_id,
            run_id=getattr(args, "run_id", None),
            force=getattr(args, "force", False),
        )
        return 0
    except Exception as exc:
        print(f"[ERROR] approve-terms failed: {exc}", file=sys.stderr)
        return 1


def cmd_translate_literal(args: argparse.Namespace, config) -> int:
    readiness_result = _warn_research_readiness(config, bounded=True)
    if readiness_result:
        return readiness_result
    try:
        translate_literal_command(
            config=config,
            chapter_id=args.chapter_id,
            block_id=args.block_id,
            run_id=getattr(args, "run_id", None),
            force=getattr(args, "force", False),
        )
        return 0
    except Exception as exc:
        print(f"[ERROR] translate-literal failed: {exc}", file=sys.stderr)
        return 1


def cmd_refine(args: argparse.Namespace, config) -> int:
    readiness_result = _warn_research_readiness(config, bounded=True)
    if readiness_result:
        return readiness_result
    try:
        refine_command(
            config=config,
            chapter_id=args.chapter_id,
            block_id=args.block_id,
            run_id=getattr(args, "run_id", None),
            style_profile=args.style_profile,
            force=getattr(args, "force", False),
        )
        return 0
    except Exception as exc:
        print(f"[ERROR] refine failed: {exc}", file=sys.stderr)
        return 1


def cmd_qa(args: argparse.Namespace, config) -> int:
    readiness_result = _warn_research_readiness(config, bounded=True)
    if readiness_result:
        return readiness_result
    try:
        qa_command(
            config=config,
            chapter_id=args.chapter_id,
            block_id=args.block_id,
            run_id=getattr(args, "run_id", None),
            style_profile=args.style_profile,
        )
        return 0
    except Exception as exc:
        print(f"[ERROR] qa failed: {exc}", file=sys.stderr)
        return 1


def cmd_format(args: argparse.Namespace, config) -> int:
    try:
        format_command(
            config=config,
            chapter_id=args.chapter_id,
            block_id=args.block_id,
            run_id=getattr(args, "run_id", None),
            force=getattr(args, "force", False),
        )
        return 0
    except Exception as exc:
        print(f"[ERROR] format failed: {exc}", file=sys.stderr)
        return 1


COMMAND_HANDLERS = {
    "run": cmd_run,
    "resume": cmd_resume,
    "status": cmd_status,
    "report": cmd_report,
    "inspect-block": cmd_inspect_block,
    "operator": cmd_operator,
    "preflight": cmd_preflight,
    "init-novel": cmd_init_novel,
    "rerun-block": cmd_rerun_block,
    "fetch": cmd_fetch,
    "scan-terms": cmd_scan_terms,
    "approve-terms": cmd_approve_terms,
    "translate-literal": cmd_translate_literal,
    "refine": cmd_refine,
    "qa": cmd_qa,
    "format": cmd_format,
}


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    configure_logging()

    try:
        config = load_app_config(args.config)
    except Exception as exc:
        print(f"[ERROR] Failed to load config: {exc}", file=sys.stderr)
        return 1

    if args.novel:
        config.novel_id = args.novel

    handler = COMMAND_HANDLERS.get(args.command)
    if handler is None:
        print(f"[ERROR] Unknown command: {args.command}", file=sys.stderr)
        return 1

    return handler(args, config)


if __name__ == "__main__":
    raise SystemExit(main())
