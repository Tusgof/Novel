"""Compatibility entrypoint; keep one authoritative Sentinel implementation."""

from pathlib import Path

_shared = Path(__file__).resolve().parents[2] / "scripts/sentinel_quality_report.py"
__file__ = str(_shared)
exec(compile(_shared.read_text(encoding="utf-8"), str(_shared), "exec"), globals())
