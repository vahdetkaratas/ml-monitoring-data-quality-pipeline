"""
Validation pipeline: run all checks, produce status and summary. MONITORING_SYSTEM_DESIGN §3, MILESTONES M2.
"""
from pathlib import Path
import json
import pandas as pd

from src.utils.paths import SCHEMA_PATH, ARTIFACTS_VALIDATION_DIR
from src.validation.load_schema import load_schema
from src.validation.schema_checks import check_required_columns, check_unknown_columns, check_column_dtypes
from src.validation.missing_checks import check_missing_rates
from src.validation.range_checks import check_ranges
from src.validation.categorical_checks import check_categorical
from src.utils.file_helpers import ensure_dir

OUTPUT_VALIDATION = ARTIFACTS_VALIDATION_DIR


def _validation_status(
    required_ok: bool,
    dtype_ok: bool,
    missing_ok: bool,
    range_ok: bool,
    cat_ok: bool,
    unknown_ok: bool,
) -> str:
    """ok / warning / critical per design."""
    if not required_ok or not dtype_ok:
        return "critical"
    if not missing_ok or not range_ok or not cat_ok or not unknown_ok:
        return "warning"
    return "ok"


def run_validation(
    df: pd.DataFrame,
    schema: dict | None = None,
    schema_path: str | Path | None = None,
) -> dict:
    """Run all validation checks. Returns summary dict with status, checks, message."""
    if schema is None:
        schema, _ = load_schema(schema_path or SCHEMA_PATH)
    if not schema:
        return {"status": "critical", "message": "Schema not loaded", "checks": {}}

    req = check_required_columns(df, schema)
    unknown = check_unknown_columns(df, schema)
    dtypes = check_column_dtypes(df, schema)
    missing = check_missing_rates(df, schema)
    ranges = check_ranges(df, schema)
    cat = check_categorical(df, schema)

    status = _validation_status(
        req["ok"],
        dtypes["ok"],
        missing["ok"],
        ranges["ok"],
        cat["ok"],
        unknown["ok"],
    )
    return {
        "status": status,
        "checks": {
            "required_columns": req,
            "unknown_columns": unknown,
            "dtypes": dtypes,
            "missing": missing,
            "ranges": ranges,
            "categorical": cat,
        },
        "message": f"Validation {status}",
    }


def run_validation_on_batch(
    batch_path: str | Path,
    output_dir: str | Path | None = None,
    schema_path: str | Path | None = None,
) -> dict:
    """Load batch CSV, run validation, optionally save summary JSON. Returns validation summary."""
    batch_path = Path(batch_path)
    df = pd.read_csv(batch_path)
    summary = run_validation(df, schema_path=schema_path)
    summary["batch_name"] = batch_path.name

    output_dir = Path(output_dir or OUTPUT_VALIDATION)
    ensure_dir(output_dir)
    out_file = output_dir / f"validation_summary_{batch_path.stem}.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    return summary
