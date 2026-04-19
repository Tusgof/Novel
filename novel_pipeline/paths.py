from __future__ import annotations

from pathlib import Path

from novel_pipeline.types import AppPaths, WorkspacePaths


def build_app_paths(root: Path) -> AppPaths:
    return WorkspacePaths.from_root(root)


def ensure_runtime_dirs(paths: AppPaths) -> None:
    for directory in [
        paths.glossary_dir,
        paths.raw_dir,
        paths.work_dir,
        paths.output_dir,
        paths.logs_dir,
    ]:
        directory.mkdir(parents=True, exist_ok=True)


__all__ = ["build_app_paths", "ensure_runtime_dirs"]
