"""Load schema definition from JSON. IMPLEMENTATION_REFERENCE §3."""
from pathlib import Path
import json

from src.utils.paths import SCHEMA_PATH


def load_schema(path: str | Path | None = None) -> tuple[dict, dict]:
    """
    Load schema_definition.json.

    Returns:
        (column_schema, file_meta): column definitions for validation, and optional file metadata.
        If the JSON contains a top-level ``__meta__`` object, it is removed from the column schema
        and returned as ``file_meta`` (e.g. ``schema_version``). Unknown columns must not use ``__meta__``.
    """
    path = Path(path or SCHEMA_PATH)
    if not path.exists():
        return {}, {}
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    if not isinstance(raw, dict):
        return {}, {}
    meta: dict = {}
    if "__meta__" in raw and isinstance(raw["__meta__"], dict):
        meta = dict(raw["__meta__"])
        raw = {k: v for k, v in raw.items() if k != "__meta__"}
    return raw, meta
