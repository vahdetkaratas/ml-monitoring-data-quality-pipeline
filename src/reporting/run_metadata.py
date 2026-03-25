"""
Lightweight run metadata for monitoring reports (no job store, no DB).
Paths are repo-relative when under REPO_ROOT for portable JSON artifacts.
"""
from __future__ import annotations

from pathlib import Path

from src.utils.paths import REPO_ROOT

# Bump when report shape or pipeline semantics change meaningfully.
PIPELINE_VERSION = "1.1.0"


def _repo_relative(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path.resolve())


def build_run_metadata(
    *,
    run_id: str,
    generated_at: str,
    n_batches: int,
    batch_index: int,
    schema_version: str | None,
    reference_dataset: Path,
    current_batch_file: Path,
) -> dict:
    """
    Fields are intentionally small and cheap to produce in-process.
    """
    return {
        "run_id": run_id,
        "generated_at": generated_at,
        "n_batches": int(n_batches),
        "batch_index": int(batch_index),
        "schema_version": schema_version,
        "pipeline_version": PIPELINE_VERSION,
        "reference_dataset": _repo_relative(reference_dataset),
        "current_batch_file": _repo_relative(current_batch_file),
    }
