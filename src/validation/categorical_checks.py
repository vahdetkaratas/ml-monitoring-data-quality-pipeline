"""Categorical checks: allowed_values, unseen categories. MONITORING_SYSTEM_DESIGN §3."""
import pandas as pd


def check_categorical(df: pd.DataFrame, schema: dict) -> dict:
    """Check category columns: only allowed values (if specified); no unseen. Returns {ok, invalid_categories, message}."""
    invalid = {}
    for col, spec in schema.items():
        if col not in df.columns or spec.get("dtype") != "category":
            continue
        allowed = spec.get("allowed_values")
        if not allowed:
            continue
        allowed_set = set(allowed)
        values = df[col].dropna().astype(str).unique()
        bad = [v for v in values if v not in allowed_set]
        if bad:
            invalid[col] = bad
    return {
        "ok": len(invalid) == 0,
        "invalid_categories": invalid,
        "message": "Categorical OK" if not invalid else f"Invalid/unseen: {invalid}",
    }
