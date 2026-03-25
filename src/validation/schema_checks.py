"""Schema checks: required columns, unknown columns, column dtypes. MONITORING_SYSTEM_DESIGN §3."""
import pandas as pd


def check_required_columns(df: pd.DataFrame, schema: dict) -> dict:
    """Check that all required columns exist. Returns {ok, missing, message}."""
    required = [c for c, spec in schema.items() if spec.get("required") is True]
    actual = set(df.columns)
    missing = [c for c in required if c not in actual]
    return {
        "ok": len(missing) == 0,
        "missing": missing,
        "message": "All required columns present" if not missing else f"Missing: {missing}",
    }


def check_unknown_columns(df: pd.DataFrame, schema: dict) -> dict:
    """
    Columns present in the batch but not declared in the schema contract.
    Policy: unknown columns produce validation **warning** (contract drift / schema creep).
    """
    unknown = [c for c in df.columns if c not in schema]
    return {
        "ok": len(unknown) == 0,
        "unknown_columns": unknown,
        "message": "No unknown columns"
        if not unknown
        else f"Columns not in schema contract: {unknown}",
    }


def check_column_dtypes(df: pd.DataFrame, schema: dict) -> dict:
    """Basic dtype check: numeric columns are numeric, etc. Returns {ok, issues, message}."""
    issues = []
    for col, spec in schema.items():
        if col not in df.columns:
            continue
        dtype = spec.get("dtype", "")
        s = df[col]
        if dtype in ("int", "float"):
            if not pd.api.types.is_numeric_dtype(s):
                try:
                    pd.to_numeric(s, errors="raise")
                except Exception:
                    issues.append(f"{col}: expected {dtype}, not numeric")
        elif dtype == "category":
            pass  # any object/string is ok for category
    return {
        "ok": len(issues) == 0,
        "issues": issues,
        "message": "Dtypes OK" if not issues else "; ".join(issues),
    }
